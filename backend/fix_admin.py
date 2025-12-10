import sys
import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Add current directory to path to allow imports
sys.path.append(os.getcwd())

try:
    from app.database import SessionLocal
    from app.models.user import User
    from app.core.security import get_password_hash
    
    def fix_admin():
        db = SessionLocal()
        try:
            username = "admin"
            password = "admin"
            
            logger.info(f"Checking for user '{username}'...")
            user = db.query(User).filter(User.username == username).first()
            
            hashed_pw = get_password_hash(password)
            
            if user:
                logger.info(f"User '{username}' found. Resetting password...")
                user.password = hashed_pw
                # Ensure role is admin
                user.role = 'admin'
            else:
                logger.info(f"User '{username}' NOT found. Creating...")
                user = User(
                    username=username,
                    password=hashed_pw,
                    role='admin',
                    full_name='Administrator',
                    is_profile_complete=True
                )
                db.add(user)
            
            db.commit()
            logger.info("----------------------------------------")
            logger.info("SUCCESS: Admin user configured.")
            logger.info(f"Username: {username}")
            logger.info(f"Password: {password}")
            logger.info("----------------------------------------")
            
        except Exception as e:
            logger.error(f"An error occurred: {e}")
            db.rollback()
        finally:
            db.close()

    if __name__ == "__main__":
        fix_admin()

except ImportError as e:
    logger.error(f"Import Error - make sure you are running this from the backend directory (e.g., inside the container in /app): {e}")
