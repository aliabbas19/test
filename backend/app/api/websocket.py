"""
WebSocket Chat API
Real-time messaging with typing indicators and read receipts
"""
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Dict, List, Set
from datetime import datetime
import json
import logging
import asyncio

from app.database import get_db, SessionLocal
from app.models.user import User
from app.models.message import Message
from app.core.security import decode_token

logger = logging.getLogger(__name__)

router = APIRouter(tags=["websocket"])


class ConnectionManager:
    """Manages WebSocket connections for real-time chat"""
    
    def __init__(self):
        # user_id -> set of WebSocket connections (user can be connected from multiple tabs)
        self.active_connections: Dict[int, Set[WebSocket]] = {}
        # user_id -> set of user_ids they're typing to
        self.typing_indicators: Dict[int, Set[int]] = {}
    
    async def connect(self, websocket: WebSocket, user_id: int):
        """Accept connection and track the user"""
        await websocket.accept()
        if user_id not in self.active_connections:
            self.active_connections[user_id] = set()
        self.active_connections[user_id].add(websocket)
        logger.info(f"User {user_id} connected. Total connections: {len(self.active_connections)}")
    
    def disconnect(self, websocket: WebSocket, user_id: int):
        """Remove connection when user disconnects"""
        if user_id in self.active_connections:
            self.active_connections[user_id].discard(websocket)
            if not self.active_connections[user_id]:
                del self.active_connections[user_id]
        logger.info(f"User {user_id} disconnected. Total connections: {len(self.active_connections)}")
    
    async def send_personal_message(self, message: dict, user_id: int):
        """Send message to a specific user (all their connections)"""
        if user_id in self.active_connections:
            disconnected = []
            for connection in self.active_connections[user_id]:
                try:
                    await connection.send_json(message)
                except Exception as e:
                    logger.warning(f"Failed to send to user {user_id}: {e}")
                    disconnected.append(connection)
            # Clean up disconnected sockets
            for conn in disconnected:
                self.active_connections[user_id].discard(conn)
    
    async def broadcast_to_class(self, message: dict, class_name: str, section_name: str = None):
        """Broadcast message to all users in a class (and optionally section)"""
        db = SessionLocal()
        try:
            query = db.query(User).filter(User.class_name == class_name)
            if section_name:
                query = query.filter(User.section_name == section_name)
            users = query.all()
            
            for user in users:
                await self.send_personal_message(message, user.id)
        finally:
            db.close()
    
    async def broadcast_to_all_students(self, message: dict):
        """Broadcast message to all connected students"""
        db = SessionLocal()
        try:
            students = db.query(User).filter(User.role == 'student').all()
            for student in students:
                await self.send_personal_message(message, student.id)
        finally:
            db.close()
    
    def is_online(self, user_id: int) -> bool:
        """Check if a user is currently online"""
        return user_id in self.active_connections and len(self.active_connections[user_id]) > 0
    
    def get_online_users(self) -> List[int]:
        """Get list of online user IDs"""
        return list(self.active_connections.keys())
    
    async def set_typing(self, from_user_id: int, to_user_id: int, is_typing: bool):
        """Set typing indicator and notify the recipient"""
        if is_typing:
            if from_user_id not in self.typing_indicators:
                self.typing_indicators[from_user_id] = set()
            self.typing_indicators[from_user_id].add(to_user_id)
        else:
            if from_user_id in self.typing_indicators:
                self.typing_indicators[from_user_id].discard(to_user_id)
        
        # Notify the recipient
        await self.send_personal_message({
            "type": "typing",
            "from_user_id": from_user_id,
            "is_typing": is_typing
        }, to_user_id)


# Global connection manager
manager = ConnectionManager()


def get_user_from_token(token: str, db: Session) -> User:
    """Validate token and return user"""
    try:
        payload = decode_token(token)
        if payload is None:
            return None
        user_id = payload.get("sub")
        if user_id is None:
            return None
        user = db.query(User).filter(User.id == int(user_id)).first()
        return user
    except Exception as e:
        logger.error(f"Token validation error: {e}")
        return None


@router.websocket("/ws/chat/{user_id}")
async def websocket_chat(
    websocket: WebSocket,
    user_id: int,
    token: str = Query(...)
):
    """
    WebSocket endpoint for real-time chat
    
    Message types:
    - message: Send a new message
    - typing: Typing indicator
    - read: Mark messages as read
    - online_status: Request online status
    """
    db = SessionLocal()
    try:
        # Authenticate user
        user = get_user_from_token(token, db)
        if not user or user.id != user_id:
            await websocket.close(code=4001, reason="Unauthorized")
            return
        
        await manager.connect(websocket, user_id)
        
        # Notify others that user is online
        await manager.send_personal_message({
            "type": "user_online",
            "user_id": user_id
        }, user_id)
        
        try:
            while True:
                # Receive message
                data = await websocket.receive_json()
                message_type = data.get("type")
                
                if message_type == "message":
                    # Handle new message
                    receiver_id = data.get("receiver_id")
                    content = data.get("content")
                    
                    if receiver_id and content:
                        # Save to database
                        new_message = Message(
                            sender_id=user_id,
                            receiver_id=receiver_id,
                            content=content
                        )
                        db.add(new_message)
                        db.commit()
                        db.refresh(new_message)
                        
                        message_data = {
                            "type": "new_message",
                            "message": {
                                "id": new_message.id,
                                "sender_id": user_id,
                                "receiver_id": receiver_id,
                                "content": content,
                                "timestamp": new_message.timestamp.isoformat(),
                                "is_read": False
                            }
                        }
                        
                        # Send to receiver
                        await manager.send_personal_message(message_data, receiver_id)
                        # Send confirmation to sender
                        await manager.send_personal_message({
                            "type": "message_sent",
                            "message_id": new_message.id,
                            "receiver_id": receiver_id
                        }, user_id)
                        
                        # Clear typing indicator
                        await manager.set_typing(user_id, receiver_id, False)
                
                elif message_type == "typing":
                    # Handle typing indicator
                    to_user_id = data.get("to_user_id")
                    is_typing = data.get("is_typing", True)
                    if to_user_id:
                        await manager.set_typing(user_id, to_user_id, is_typing)
                
                elif message_type == "read":
                    # Mark messages as read
                    message_ids = data.get("message_ids", [])
                    sender_id = data.get("sender_id")
                    
                    if message_ids:
                        now = datetime.utcnow()
                        db.query(Message).filter(
                            Message.id.in_(message_ids),
                            Message.receiver_id == user_id
                        ).update({
                            Message.is_read: True,
                            Message.read_at: now
                        }, synchronize_session=False)
                        db.commit()
                        
                        # Notify sender that messages were read
                        if sender_id:
                            await manager.send_personal_message({
                                "type": "messages_read",
                                "message_ids": message_ids,
                                "read_by": user_id,
                                "read_at": now.isoformat()
                            }, sender_id)
                
                elif message_type == "online_status":
                    # Return online status of requested users
                    user_ids = data.get("user_ids", [])
                    online_status = {
                        uid: manager.is_online(uid) for uid in user_ids
                    }
                    await websocket.send_json({
                        "type": "online_status",
                        "status": online_status
                    })
                
                elif message_type == "broadcast" and user.role == "admin":
                    # Admin broadcast to specific class or all students
                    content = data.get("content")
                    target_class = data.get("class_name")
                    target_section = data.get("section_name")
                    
                    if content:
                        broadcast_msg = {
                            "type": "broadcast_message",
                            "content": content,
                            "from_admin": True,
                            "timestamp": datetime.utcnow().isoformat()
                        }
                        
                        if target_class:
                            await manager.broadcast_to_class(broadcast_msg, target_class, target_section)
                        else:
                            await manager.broadcast_to_all_students(broadcast_msg)
        
        except WebSocketDisconnect:
            manager.disconnect(websocket, user_id)
            # Notify others that user is offline
            await manager.send_personal_message({
                "type": "user_offline",
                "user_id": user_id
            }, user_id)
    
    except Exception as e:
        logger.exception(f"WebSocket error for user {user_id}: {e}")
        manager.disconnect(websocket, user_id)
    finally:
        db.close()


@router.get("/api/chat/online-users")
async def get_online_users(db: Session = Depends(get_db)):
    """Get list of currently online user IDs"""
    return {"online_users": manager.get_online_users()}


@router.get("/api/chat/unread-count")
async def get_unread_count(
    user_id: int,
    db: Session = Depends(get_db)
):
    """Get count of unread messages for a user"""
    count = db.query(Message).filter(
        Message.receiver_id == user_id,
        Message.is_read == False
    ).count()
    return {"unread_count": count}
