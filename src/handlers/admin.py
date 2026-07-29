from aiogram import Router, types
from aiogram.filters import Command, CommandObject
from src.services.db import db
from src.services.llm import llm
from src.utils.logger import logger
import os
from datetime import datetime

router = Router()

def is_admin(user_id: int) -> bool:
    """Cek apakah user adalah admin"""
    admin_ids = os.getenv("ADMIN_IDS", "").split(",")
    return str(user_id) in admin_ids

@router.message(Command("stats"))
async def cmd_stats(message: types.Message):
    """Lihat statistik (admin only)"""
    if not is_admin(message.from_user.id):
        await message.answer("⛔ Hanya admin yang bisa melihat statistik.")
        return
    
    chat_stats = db.get_chat_stats()
    feedback_stats = db.get_feedback_stats()
    faq_count = len(db.get_all_faq())
    
    # Ambil user terbaru
    users = db.get_all_users()
    recent_users = users[:5] if users else []
    
    text = f"""
📊 <b>Dashboard Admin</b>

<b>👥 User:</b>
Total: {chat_stats['total_users']}
Terbaru: 
"""
    for u in recent_users:
        text += f"  • {u['first_name']} (@{u['username']})\n"
    
    text += f"""
<b>💬 Chat:</b>
Total: {chat_stats['total_chats']}
Hari Ini: {chat_stats['today_chats']}

<b>📚 FAQ:</b>
Total: {faq_count}

<b>💬 Feedback:</b>
Total: {feedback_stats['total_feedback']}
Rating Rata-rata: {feedback_stats['average_rating']}/5

📅 {datetime.now().strftime('%d %B %Y %H:%M')}
"""
    
    await message.answer(text, parse_mode="HTML")

@router.message(Command("addfaq"))
async def cmd_addfaq(message: types.Message, command: CommandObject):
    """Tambah FAQ (admin only)"""
    if not is_admin(message.from_user.id):
        await message.answer("⛔ Hanya admin yang bisa menambah FAQ.")
        return
    
    if not command.args:
        await message.answer(
            "❌ <b>Format salah!</b>\n\n"
            "Gunakan:\n"
            "/addfaq pertanyaan | jawaban\n\n"
            "Contoh:\n"
            "/addfaq Apa itu P5? | Projek Penguatan Profil Pelajar Pancasila",
            parse_mode="HTML"
        )
        return
    
    try:
        parts = command.args.split(" | ")
        if len(parts) < 2:
            raise ValueError("Format tidak lengkap")
        
        question = parts[0].strip()
        answer = " | ".join(parts[1:]).strip()
        
        if not question or not answer:
            raise ValueError("Pertanyaan atau jawaban kosong")
        
        db.add_faq(question, answer)
        
        await message.answer(
            f"✅ <b>FAQ berhasil ditambahkan!</b>\n\n"
            f"❓ {question}\n"
            f"✅ {answer[:100]}{'...' if len(answer) > 100 else ''}",
            parse_mode="HTML"
        )
        logger.info(f"FAQ added by admin {message.from_user.id}: {question}")
        
    except Exception as e:
        await message.answer(f"❌ Error: {str(e)}")

@router.message(Command("listfaq"))
async def cmd_listfaq(message: types.Message):
    """Lihat semua FAQ dengan ID (admin only)"""
    if not is_admin(message.from_user.id):
        await message.answer("⛔ Hanya admin.")
        return
    
    faqs = db.get_all_faq()
    
    if not faqs:
        await message.answer("Belum ada FAQ.")
        return
    
    text = "📋 <b>Daftar FAQ (ID | Pertanyaan)</b>\n\n"
    for faq in faqs[:30]:
        text += f"{faq['id']}. {faq['question']}\n"
    
    if len(faqs) > 30:
        text += f"\n... dan {len(faqs) - 30} FAQ lainnya"