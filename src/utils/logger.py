from loguru import logger
import sys

# Konfigurasi logging yang keren
logger.remove()  # Hapus default handler
logger.add(
    sys.stdout,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
    level="INFO"
)
logger.add(
    "logs/bot.log",
    rotation="500 MB",
    retention="10 days",
    format="{time} | {level} | {message}",
    level="DEBUG"
)

# Export logger
__all__ = ["logger"]