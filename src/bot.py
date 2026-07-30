from aiogram import Bot, Dispatcher
from aiogram.types import BotCommand
from aiogram.client.default import DefaultBotProperties
import os
from dotenv import load_dotenv
from utils.logger import logger

# Load environment variables
load_dotenv()

# Initialize bot
BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN is required in .env file")

bot = Bot(
    token=BOT_TOKEN,
    default=DefaultBotProperties(parse_mode="HTML")
)

# Initialize dispatcher
dp = Dispatcher()

# Import and register handlers
from handlers import start, faq, ai_chat, admin

dp.include_router(start.router)
dp.include_router(faq.router)
dp.include_router(ai_chat.router)
dp.include_router(admin.router)

logger.info("Bot handlers registered successfully")

async def set_commands():
    """Set menu commands di Telegram"""
    commands = [
        BotCommand(command="start", description="🚀 Mulai bot"),
        BotCommand(command="help", description="❓ Bantuan"),
        BotCommand(command="ai", description="🤖 Chat dengan AI"),
        BotCommand(command="faq", description="📚 Lihat FAQ"),
        BotCommand(command="feedback", description="💬 Kirim saran"),
    ]
    
    # Admin commands
    admin_ids = os.getenv("ADMIN_IDS", "").split(",")
    if admin_ids:
        admin_commands = [
            BotCommand(command="stats", description="📊 Statistik bot"),
            BotCommand(command="addfaq", description="➕ Tambah FAQ"),
            BotCommand(command="listfaq", description="📋 Daftar FAQ"),
            BotCommand(command="broadcast", description="📢 Kirim pengumuman"),
        ]
        commands.extend(admin_commands)
    
    await bot.set_my_commands(commands)
    logger.info("Bot commands set")
