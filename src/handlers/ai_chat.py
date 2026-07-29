from aiogram import Router, types
from aiogram.filters import Command
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from src.services.llm import llm
from src.services.db import db
from src.utils.logger import logger
import os

router = Router()

class AIChatState(StatesGroup):
    """State untuk AI chat mode"""
    active = State()

@router.message(Command("ai"))
async def start_ai_chat(message: types.Message, state: FSMContext):
    """Mulai mode AI chat"""
    await state.set_state(AIChatState.active)
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="❌ Keluar", callback_data="exit_ai")]
    ])
    
    await message.answer(
        "🤖 <b>Mode AI Aktif!</b>\n\n"
        "Saya siap membantu menjawab pertanyaan tentang:\n"
        "• Materi pelajaran\n"
        "• Metode mengajar\n"
        "• Komunikasi dengan orang tua\n"
        "• Administrasi guru\n\n"
        "Kirim pertanyaanmu sekarang!\n"
        "Klik tombol di bawah untuk keluar.",
        reply_markup=keyboard,
        parse_mode="HTML"
    )
    
    logger.info(f"AI mode started for user {message.from_user.id}")

@router.message(AIChatState.active)
async def handle_ai_chat(message: types.Message, state: FSMContext):
    """Handle pesan di mode AI"""
    # Keluar dari mode AI
    if message.text == "/exit":
        await state.clear()
        await message.answer("👋 Keluar dari mode AI. Ketik /ai kalo butuh lagi.")
        return
    
    # Proses pertanyaan
    await message.bot.send_chat_action(message.chat.id, "typing")
    
    # Ambil history terakhir (konteks)
    history = db.get_chat_history(message.from_user.id, limit=3)
    context = ""
    if history:
        last_q = history[0]['question'][:100]
        context = f"Pertanyaan sebelumnya: {last_q}"
    
    # Dapatkan response dari AI
    response = await llm.chat(message.text, context=context)
    
    # Simpan ke database
    db.save_user(
        user_id=message.from_user.id,
        username=message.from_user.username,
        first_name=message.from_user.first_name
    )
    db.save_chat(message.from_user.id, message.text, response)
    
    # Kirim balasan
    if len(response) > 4000:
        # Split kalo panjang
        for i in range(0, len(response), 4000):
            await message.answer(response[i:i+4000])
    else:
        await message.answer(response)
    
    # Tawarkan bantuan tambahan
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="❓ FAQ", callback_data="ai_faq"),
            InlineKeyboardButton(text="📝 Quiz", callback_data="ai_quiz")
        ],
        [InlineKeyboardButton(text="❌ Keluar AI", callback_data="exit_ai")]
    ])
    
    await message.answer(
        "💡 Butuh bantuan lain? Pilih menu di bawah:",
        reply_markup=keyboard
    )

@router.callback_query(lambda c: c.data == "exit_ai")
async def exit_ai_callback(callback: types.CallbackQuery, state: FSMContext):
    """Keluar dari mode AI via callback"""
    await state.clear()
    await callback.message.edit_text("👋 Keluar dari mode AI.")
    await callback.message.answer("Ketik /ai kalo mau chat lagi.")
    await callback.answer()

@router.callback_query(lambda c: c.data == "ai_faq")
async def ai_faq_callback(callback: types.CallbackQuery):
    """Tawarkan bantuan FAQ"""
    await callback.message.answer(
        "📚 Coba tanyakan pertanyaan langsung (tanpa /ai).\n"
        "Saya akan cek di database FAQ."
    )
    await callback.answer()

@router.callback_query(lambda c: c.data == "ai_quiz")
async def ai_quiz_callback(callback: types.CallbackQuery):
    """Generate quiz dari AI"""
    await callback.message.answer(
        "📝 <b>Generate Quiz</b>\n\n"
        "Kirim: <b>topik | tingkat</b>\n"
        "Contoh: Matematika SMA | IPA SMP",
        parse_mode="HTML"
    )
    await callback.answer()