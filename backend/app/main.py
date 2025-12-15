"""
FastAPI application entry point
"""
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
import time
from app.config import settings
from app.database import engine, Base
from app.api import auth, videos, uploads, comments, ratings, messages, users, admin, posts, reports
from app.core.rate_limit import rate_limit_middleware
from app.core.metrics import request_metrics
from contextlib import asynccontextmanager
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from app.core.scheduler import scheduled_send_champions, auto_archive_videos
from fastapi.staticfiles import StaticFiles
import os

from sqlalchemy.exc import OperationalError
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create uploads directory if not exists
os.makedirs(settings.UPLOAD_FOLDER, exist_ok=True)

# Initialize Scheduler
scheduler = BackgroundScheduler()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Initialize DB and Scheduler
    
    # Start Scheduler
    # Weekly Champions Report (Wed 8 PM)
    scheduler.add_job(
        scheduled_send_champions,
        trigger=CronTrigger(day_of_week='wed', hour=20, minute=0),
        id='weekly_champions_telegram',
        name='Send weekly champions to Telegram',
        replace_existing=True
    )
    
    # Auto Archive Videos (Daily at Midnight)
    scheduler.add_job(
        auto_archive_videos,
        trigger=CronTrigger(hour=0, minute=0),
        id='auto_archive_videos',
        name='Auto archive old videos',
        replace_existing=True
    )
    
    scheduler.start()
    logger.info("Scheduler started with weekly champions job and daily auto-archive.")
    
    yield
    
    # Shutdown
    scheduler.shutdown()
    logger.info("Scheduler shut down.")

# Create database tables with retry logic
max_retries = 30
retry_delay = 2

for attempt in range(max_retries):
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully")
        break
    except OperationalError as e:
        if attempt < max_retries - 1:
            logger.warning(f"Database not ready (attempt {attempt + 1}/{max_retries}): {e}")
            logger.info(f"Retrying in {retry_delay} seconds...")
            time.sleep(retry_delay)
        else:
            logger.error("Failed to connect to database after multiple attempts")
            raise e

# Create initial data
try:
    from app.database import SessionLocal
    from app.models.user import User
    from app.core.security import get_password_hash
    
    db = SessionLocal()
    try:
        admin_user = db.query(User).filter(User.username == "admin").first()
        if not admin_user:
            logger.info("Creating default admin user...")
            admin_user = User(
                username="admin",
                password=get_password_hash("admin"),
                role="admin",
                full_name="Administrator"
            )
            db.add(admin_user)
            db.commit()
            logger.info("Default admin user created (username: admin, password: admin)")
        else:
            logger.info("Admin user already exists")
    except Exception as e:
        logger.error(f"Error creating initial data: {e}")
    finally:
        db.close()
except Exception as e:
    logger.error(f"Failed to execute initial setup: {e}")


# Initialize FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Trusted host middleware (in production)
if not settings.DEBUG:
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=["basamaljanaby.com", "*.basamaljanaby.com", "localhost", "127.0.0.1"]
    )

# Rate limiting middleware
@app.middleware("http")
async def rate_limit(request: Request, call_next):
    return await rate_limit_middleware(request, call_next)


# Request metrics middleware
@app.middleware("http")
async def track_metrics(request: Request, call_next):
    """Track request metrics for performance monitoring"""
    start_time = time.time()
    response = await call_next(request)
    duration_ms = (time.time() - start_time) * 1000  # Convert to milliseconds
    request_metrics.add(
        endpoint=request.url.path,
        duration_ms=duration_ms,
        status_code=response.status_code
    )
    return response

# Include routers
app.include_router(auth.router)
app.include_router(videos.router)
app.include_router(uploads.router)
app.include_router(comments.router)
app.include_router(ratings.router)
app.include_router(messages.router)
app.include_router(users.router)
app.include_router(admin.router)
app.include_router(posts.router)
app.include_router(reports.router)

# Mount static files (Legacy path)
app.mount("/data/uploads", StaticFiles(directory=settings.UPLOAD_FOLDER), name="uploads")

# Mount static assets (images)
import pathlib
assets_images_path = pathlib.Path(__file__).parent / "assets" / "images"
if assets_images_path.exists():
    app.mount("/assets/images", StaticFiles(directory=str(assets_images_path)), name="assets_images")


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Basam Al Janaby Platform API",
        "version": settings.APP_VERSION,
        "docs": "/docs"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}

