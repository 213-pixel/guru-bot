from aiogram import Router, types
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from src.services.db import db
from src.utils.logger import logger

router = Router()

@router.message(Command("start"))
async def cmd_start(message: types.Message):
    """Handler untuk /start"""
    user = message.from_user
    
    # Simpan user ke database
    db.save_user(
        user_id=user.id,
        username=user.username,
        first_name=user.first_name,
        last_name=user.last_name
    )
    
    logger.info(f"User {user.id} started bot")
    
    # Keyboard menu
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="📚 FAQ", callback_data="menu_faq"),
            InlineKeyboardButton(text="🤖 Tanya AI", callback_data="menu_ai")
        ],
        [
            InlineKeyboardButton(text="📊 Statistik", callback_data="menu_stats"),
            InlineKeyboardButton(text="💬 Feedback", callback_data="menu_feedback")
        ]
    ])
    
    welcome_text = f"""
👋 <b>Halo {user.first_name}!</b>

Selamat datang di <b>Guru Assistant Bot</b> 🎓

Saya adalah asisten AI yang siap membantu pekerjaan administrasi guru:

✅ <b>Menjawab FAQ</b> - Cepat dan praktis
✅ <b>Tanya AI</b> - Untuk pertanyaan kompleks
✅ <b>Administrasi</b> - Bantuan tugas guru

<b>Cara menggunakan:</b>
• Ketik pertanyaan langsung untuk FAQ
• Gunakan /ai untuk chat dengan AI
• Gunakan /faq untuk lihat daftar pertanyaan

Selamat menggunakan! 🚀
"""
    
    await message.answer(welcome_text, reply_markup=keyboard, parse_mode="HTML")

@router.message(Command("help"))
async def cmd_help(message: types.Message):
    """Handler untuk /help"""
    help_text = """
❓ <b>Panduan Penggunaan</b>

<b>Perintah Dasar:</b>
/start - Mulai bot
/help - Tampilkan bantuan ini
/ai - Mode chat dengan AI
/faq - Lihat daftar FAQ
/feedback - Kirim saran

<b>Tips:</b>
• Tanyakan pertanyaan langsung untuk jawaban cepat
• Gunakan /ai untuk pertanyaan kompleks
• Admin bisa menambah FAQ dengan /addfaq

<b>Contoh pertanyaan:</b>
• "Apa itu metode pembelajaran aktif?"
• "Cara mengatasi siswa malas?"
• "Bagaimana berkomunikasi dengan orang tua?"

Butuh bantuan? Hubungi admin melalui /feedback
"""
    await message.answer(help_text, parse_mode="HTML")

@router.callback_query(lambda c: c.data.startswith("menu_"))
async def menu_callback(callback: types.CallbackQuery):
    """Handle menu buttons"""
    action = callback.data.replace("menu_", "")
    
    if action == "faq":
        await callback.message.answer("📚 Ketik pertanyaanmu, saya akan cari di FAQ.")
    
    elif action == "ai":
        await callback.message.answer("🤖 Mode AI aktif! Kirim pertanyaanmu.")
        # Trigger AI mode via command
        from src.handlers.ai_chat import start_ai_chat
        await start_ai_chat(callback.message, None)
    
    elif action == "stats":
        stats = db.get_chat_stats()
        text = f"""
📊 <b>Statistik Bot</b>

👥 Total Pengguna: {stats['total_users']}
💬 Total Chat: {stats['total_chats']}
📈 Chat Hari Ini: {stats['today_chats']}
"""
        await callback.message.answer(text, parse_mode="HTML")
    
    elif action == "feedback":
        await callback.message.answer(
            "💬 <b>Kirim Feedback</b>\n\n"
            "Ketik saran atau masukanmu. Saya akan terus berkembang! 🙏",
            parse_mode="HTML"
        )
    
    await callback.answer()