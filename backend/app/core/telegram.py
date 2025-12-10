"""
Telegram integration for sending messages
"""
import urllib.request
import urllib.parse
import json
import os
from typing import Optional
from app.config import settings


def send_telegram_message(bot_token: str, chat_id: str, message: str) -> bool:
    """
    Send a message to Telegram
    
    Args:
        bot_token: Telegram bot token
        chat_id: Telegram chat ID
        message: Message text
    
    Returns:
        True if successful, False otherwise
    """
    try:
        url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        data = {
            'chat_id': chat_id,
            'text': message
        }
        
        req = urllib.request.Request(
            url,
            data=urllib.parse.urlencode(data).encode(),
            headers={'Content-Type': 'application/x-www-form-urlencoded'}
        )
        
        with urllib.request.urlopen(req, timeout=10) as response:
            result = json.loads(response.read().decode())
            return result.get('ok', False)
    except Exception as e:
        print(f"Error sending Telegram message: {e}")
        return False


def send_telegram_document(bot_token: str, chat_id: str, file_path: str, caption: str = "") -> bool:
    """
    Send a document/file to Telegram
    
    Args:
        bot_token: Telegram bot token
        chat_id: Telegram chat ID
        file_path: Path to file to send
        caption: Optional caption
    
    Returns:
        True if successful, False otherwise
    """
    try:
        import os
        if not os.path.exists(file_path):
            return False
        
        url = f"https://api.telegram.org/bot{bot_token}/sendDocument"
        
        with open(file_path, 'rb') as f:
            files = {'document': f}
            data = {
                'chat_id': chat_id,
                'caption': caption
            }
            
            # Use requests-like approach with urllib
            import mimetypes
            content_type, _ = mimetypes.guess_type(file_path)
            if not content_type:
                content_type = 'application/octet-stream'
            
            # Create multipart form data
            boundary = '----WebKitFormBoundary7MA4YWxkTrZu0gW'
            body = []
            
            for key, value in data.items():
                body.append(f'--{boundary}'.encode())
                body.append(f'Content-Disposition: form-data; name="{key}"'.encode())
                body.append(b'')
                body.append(str(value).encode())
            
            body.append(f'--{boundary}'.encode())
            body.append(f'Content-Disposition: form-data; name="document"; filename="{os.path.basename(file_path)}"'.encode())
            body.append(f'Content-Type: {content_type}'.encode())
            body.append(b'')
            body.append(open(file_path, 'rb').read())
            body.append(f'--{boundary}--'.encode())
            
            req = urllib.request.Request(
                url,
                data=b'\r\n'.join(body),
                headers={'Content-Type': f'multipart/form-data; boundary={boundary}'}
            )
            
            with urllib.request.urlopen(req, timeout=30) as response:
                result = json.loads(response.read().decode())
                return result.get('ok', False)
    except Exception as e:
        print(f"Error sending Telegram document: {e}")
        return False


def get_telegram_settings_from_env() -> Optional[dict]:
    """
    Get Telegram settings from environment variables
    
    Returns:
        Dict with bot_token and chat_id, or None if not configured
    """
    bot_token = settings.TELEGRAM_BOT_TOKEN
    chat_id = settings.TELEGRAM_CHAT_ID
    
    if bot_token and chat_id:
        return {
            'bot_token': bot_token,
            'chat_id': chat_id
        }
    
    return None

