from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram import Bot, Dispatcher, executor
from middlewares.auth import AuthMiddleware
from config import BOT_TOKEN, DATABASE_URL
from tortoise import Tortoise
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize bot and dispatcher
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)

# Add middlewares
dp.middleware.setup(LoggingMiddleware())
dp.middleware.setup(AuthMiddleware())


async def on_startup(dp):
    """Tortoise ORM initialization"""
    await Tortoise.init(
        db_url=DATABASE_URL,
        modules={'models': ['database.models']}
    )
    logger.info("Database connection established")


async def on_shutdown(dp):
    """Cleanup"""
    await Tortoise.close_connections()
    logger.info("Database connection closed")


if __name__ == '__main__':
    from handlers import *  # This will import all handlers

    executor.start_polling(dp, on_startup=on_startup, on_shutdown=on_shutdown)
