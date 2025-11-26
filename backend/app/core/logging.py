import logging
import sys
from pathlib import Path
from loguru import logger
from app.core.config import settings

# Remove default handler
logger.remove()

# Add custom handler with rotation
log_path = Path("logs")
log_path.mkdir(exist_ok=True)

# Console handler
logger.add(
    sys.stdout,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
    level=settings.LOG_LEVEL,
    colorize=True,
)

# File handler with rotation
logger.add(
    log_path / "app_{time:YYYY-MM-DD}.log",
    rotation="00:00",
    retention="30 days",
    compression="zip",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
    level=settings.LOG_LEVEL,
)

# JSON handler for production
if settings.ENVIRONMENT == "production":
    logger.add(
        log_path / "app_{time:YYYY-MM-DD}.json",
        rotation="00:00",
        retention="30 days",
        compression="zip",
        serialize=True,
        level="INFO",
    )

def get_logger(name: str):
    """Get a logger instance for a module"""
    return logger.bind(name=name)
