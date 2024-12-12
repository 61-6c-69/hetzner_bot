import os
import uuid
from fastapi import UploadFile
from datetime import datetime
from config import UPLOAD_DIR

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'pdf', 'txt', 'doc', 'docx'}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB


def allowed_file(filename: str) -> bool:
    """Check if file extension is allowed"""
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def get_file_extension(filename: str) -> str:
    """Get file extension"""
    return filename.rsplit('.', 1)[1].lower() if '.' in filename else ''


def get_safe_filename(filename: str) -> str:
    """Generate a safe filename"""
    ext = get_file_extension(filename)
    return f"{uuid.uuid4().hex}.{ext}"


async def save_ticket_file(file: UploadFile, user_id: int) -> str:
    """Save uploaded ticket file
    Returns the relative path to the saved file
    """
    if not file:
        return None

    # Check file size
    file.file.seek(0, 2)  # Seek to end
    size = file.file.tell()
    file.file.seek(0)  # Seek back to start

    if size > MAX_FILE_SIZE:
        raise ValueError("File too large")

    # Check file extension
    if not allowed_file(file.filename):
        raise ValueError("File type not allowed")

    # Create user upload directory if it doesn't exist
    user_dir = os.path.join(UPLOAD_DIR, str(user_id))
    os.makedirs(user_dir, exist_ok=True)

    # Generate safe filename
    filename = get_safe_filename(file.filename)

    # Create date-based subdirectory
    date_dir = datetime.utcnow().strftime('%Y/%m/%d')
    save_dir = os.path.join(user_dir, date_dir)
    os.makedirs(save_dir, exist_ok=True)

    # Save file
    file_path = os.path.join(save_dir, filename)
    with open(file_path, 'wb') as f:
        content = await file.read()
        f.write(content)

    # Return relative path from UPLOAD_DIR
    return os.path.relpath(file_path, UPLOAD_DIR)


async def delete_file(file_path: str) -> bool:
    """Delete a file
    file_path should be relative to UPLOAD_DIR
    """
    if not file_path:
        return False

    full_path = os.path.join(UPLOAD_DIR, file_path)
    try:
        if os.path.exists(full_path):
            os.remove(full_path)
            return True
    except Exception:
        pass
    return False


def get_file_url(file_path: str) -> str:
    """Get public URL for a file
    file_path should be relative to UPLOAD_DIR
    """
    if not file_path:
        return None
    return f"/uploads/{file_path}"
