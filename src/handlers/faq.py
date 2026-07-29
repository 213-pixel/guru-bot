from aiogram import Router, types
from aiogram.filters import Command, StateFilter
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from src.services.db import db
from src.services.llm import llm
from src.utils.logger import logger
import re

router = Router()

class FAQState(StatesGroup):
    waiting_for_question = State()

@router.message(Command("faq"))
async def cmd_faq(message: types.Message):
    """Lihat semua FAQ"""
    faqs = db.get_all_faq()
    
    if not faqs:
        await message.answer(
            "📚 <b>Belum ada FAQ</b>\n\n"
            "Admin bisa menambahkan FAQ dengan:\n"
            "/addfaq [pertanyaan] | [jawaban]",
            parse_mode="HTML"
        )
        return
    
    text = "📚 <b>Daftar FAQ</b>\n\n"
    for idx, faq in enumerate(faqs[:20], 1):
        text += f"{idx}. {faq['question'][:50]}...\n"
    
    text += f"\nTotal: {len(faqs)} FAQ\nKetik pertanyaan untuk mencari."
    
    await message.answer(text, parse_mode="HTML")

@router.message(StateFilter(None))
async def handle_faq_query(message: types.Message):
    """Cek apakah pertanyaan ada di FAQ"""
    # Skip kalo command
    if message.text.startswith('/'):
        return
    
    # Skip kalo terlalu pendek
    if len(message.text) < 5:
        return
    
    # Cari di FAQ
    answer = db.get_faq(message.text)
    
    if answer:
        # Tambahkan user ke database
        db.save_user(
            user_id=message.from_user.id,
            username=message.from_user.username,
            first_name=message.from_user.first_name
        )
        
        # Kirim jawaban FAQ
        await message.answer(
            f"📌 <b>Jawaban:</b>\n\n{answer}",
            parse_mode="HTML"
        )
        logger.info(f"FAQ answered for user {message.from_user.id}")
        return
    
    # Kalo gak ada di FAQ, tawarkan AI
    await message.answer(
        "🤔 Pertanyaanmu belum ada di FAQ.\n\n"
        "Ketik <b>/ai</b> untuk bertanya ke AI, atau\n"
        "Tunggu admin akan menambahkan pertanyaan ini.",
        parse_mode="HTML"
    )
    
    # Tawarkan untuk tambah ke FAQ (admin only)
    admin_ids = [int(id) for id in os.getenv("ADMIN_IDS", "").split(",") if id]
    if message.from_user.id in admin_ids:
        await message.answer(
            "💡 <b>Admin:</b> Mau tambahkan ini ke FAQ?\n"
            f"Ketik: /addfaq {message.text} | [jawaban]",
            parse_mode="HTML"
        )