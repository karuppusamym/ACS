"""Input validation utilities"""
import re
from typing import Optional
from pydantic import validator, BaseModel, EmailStr, Field


def validate_password_strength(password: str) -> str:
    """
    Validate password meets security requirements:
    - At least 8 characters
    - Contains uppercase and lowercase
    - Contains at least one number
    - Contains at least one special character
    """
    if len(password) < 8:
        raise ValueError("Password must be at least 8 characters long")

    if not re.search(r"[A-Z]", password):
        raise ValueError("Password must contain at least one uppercase letter")

    if not re.search(r"[a-z]", password):
        raise ValueError("Password must contain at least one lowercase letter")

    if not re.search(r"\d", password):
        raise ValueError("Password must contain at least one number")

    if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
        raise ValueError("Password must contain at least one special character")

    return password


def validate_username(username: str) -> str:
    """
    Validate username:
    - 3-50 characters
    - Alphanumeric, underscore, hyphen only
    - Must start with letter
    """
    if len(username) < 3 or len(username) > 50:
        raise ValueError("Username must be between 3 and 50 characters")

    if not re.match(r"^[a-zA-Z][a-zA-Z0-9_-]*$", username):
        raise ValueError("Username must start with a letter and contain only letters, numbers, underscores, and hyphens")

    return username


def validate_connection_name(name: str) -> str:
    """
    Validate database connection name:
    - 1-100 characters
    - No special characters that could cause issues
    """
    if len(name) < 1 or len(name) > 100:
        raise ValueError("Connection name must be between 1 and 100 characters")

    if not re.match(r"^[a-zA-Z0-9_\- ]+$", name):
        raise ValueError("Connection name can only contain letters, numbers, spaces, underscores, and hyphens")

    return name


def validate_table_name(table_name: str) -> str:
    """
    Validate table name to prevent SQL injection:
    - Alphanumeric, underscore only
    - Must start with letter or underscore
    - 1-128 characters
    """
    if len(table_name) < 1 or len(table_name) > 128:
        raise ValueError("Table name must be between 1 and 128 characters")

    if not re.match(r"^[a-zA-Z_][a-zA-Z0-9_]*$", table_name):
        raise ValueError("Invalid table name format")

    return table_name


def validate_url(url: str) -> str:
    """Validate URL format"""
    url_pattern = re.compile(
        r'^https?://'  # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain...
        r'localhost|'  # localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
        r'(?::\d+)?'  # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)

    if not url_pattern.match(url):
        raise ValueError("Invalid URL format")

    return url


def sanitize_filename(filename: str) -> str:
    """
    Sanitize filename to prevent path traversal:
    - Remove path separators
    - Remove null bytes
    - Limit length
    """
    # Remove path separators
    filename = filename.replace("/", "").replace("\\", "")

    # Remove null bytes
    filename = filename.replace("\0", "")

    # Remove leading/trailing dots and spaces
    filename = filename.strip(". ")

    # Limit length
    if len(filename) > 255:
        filename = filename[:255]

    if not filename:
        raise ValueError("Invalid filename")

    return filename


def validate_port(port: int) -> int:
    """Validate port number"""
    if port < 1 or port > 65535:
        raise ValueError("Port must be between 1 and 65535")
    return port


class ValidatedPasswordMixin(BaseModel):
    """Mixin for models that need password validation"""

    @validator('password')
    def password_strength(cls, v):
        return validate_password_strength(v)


class ValidatedUsernameMixin(BaseModel):
    """Mixin for models that need username validation"""

    @validator('username')
    def username_format(cls, v):
        return validate_username(v)
