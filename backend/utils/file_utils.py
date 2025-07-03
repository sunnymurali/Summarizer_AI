import os
import mimetypes
from typing import Optional

# Supported file types
SUPPORTED_EXTENSIONS = {'.pdf', '.txt', '.docx'}
SUPPORTED_MIMETYPES = {
    'application/pdf',
    'text/plain',
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
    'application/msword'
}

def validate_file_type(filename: str) -> bool:
    """Validate if the file type is supported"""
    if not filename:
        return False
    
    # Check file extension
    file_extension = os.path.splitext(filename)[1].lower()
    return file_extension in SUPPORTED_EXTENSIONS

def get_file_extension(filename: str) -> str:
    """Get the file extension from filename"""
    if not filename:
        return ""
    
    return os.path.splitext(filename)[1].lower()

def get_mime_type(filename: str) -> Optional[str]:
    """Get the MIME type of a file"""
    if not filename:
        return None
    
    mime_type, _ = mimetypes.guess_type(filename)
    return mime_type

def is_supported_mime_type(mime_type: str) -> bool:
    """Check if the MIME type is supported"""
    return mime_type in SUPPORTED_MIMETYPES

def get_file_size_mb(file_path: str) -> float:
    """Get file size in MB"""
    try:
        size_bytes = os.path.getsize(file_path)
        return size_bytes / (1024 * 1024)
    except OSError:
        return 0.0

def validate_file_size(file_path: str, max_size_mb: float = 50.0) -> bool:
    """Validate file size (default max 50MB)"""
    try:
        size_mb = get_file_size_mb(file_path)
        return size_mb <= max_size_mb
    except:
        return False

def safe_filename(filename: str) -> str:
    """Create a safe filename by removing/replacing unsafe characters"""
    if not filename:
        return "unnamed_file"
    
    # Remove path components
    filename = os.path.basename(filename)
    
    # Replace unsafe characters
    unsafe_chars = '<>:"/\\|?*'
    for char in unsafe_chars:
        filename = filename.replace(char, '_')
    
    # Remove multiple consecutive underscores
    while '__' in filename:
        filename = filename.replace('__', '_')
    
    # Remove leading/trailing underscores and dots
    filename = filename.strip('_.')
    
    # Ensure filename is not empty
    if not filename:
        return "unnamed_file"
    
    return filename

def get_supported_extensions() -> list:
    """Get list of supported file extensions"""
    return list(SUPPORTED_EXTENSIONS)

def get_file_info(filename: str) -> dict:
    """Get comprehensive file information"""
    return {
        "filename": filename,
        "extension": get_file_extension(filename),
        "mime_type": get_mime_type(filename),
        "is_supported": validate_file_type(filename),
        "safe_filename": safe_filename(filename)
    }
