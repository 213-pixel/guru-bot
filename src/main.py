from fastapi import FastAPI, Request, Response, BackgroundTasks # 1. Import BackgroundTasks
from fastapi.responses import JSONResponse
from aiogram.types import Update
import uvicorn
import os
from dotenv import load_dotenv
from bot import bot, dp
from utils.logger import logger

load_dotenv()

app = FastAPI(
    title="Guru Assistant Bot API",
    description="Telegram Bot untuk membantu administrasi guru",
    version="1.0.0"
)

# Helper function untuk memproses update di background
async def process_update(update_data: dict):
    try:
        update = Update.model_validate(update_data, context={"bot": bot})
        await dp.feed_update(bot, update)
    except Exception as e:
        logger.error(f"Error processing update: {e}")

@app.post("/webhook")
async def webhook(request: Request, background_tasks: BackgroundTasks):
    """
    Endpoint untuk menerima update dari Telegram
    """
    try:
        # 1. Parse request body
        body = await request.json()
        
        # 2. Lempar proses pemrosesan pesan ke Background Task
        background_tasks.add_task(process_update, body)
        
        # 3. Langsung kembalikan 200 OK ke Telegram dalam hitungan milidetik
        return JSONResponse(content={"status": "ok"})
        
    except Exception as e:
        logger.error(f"Webhook error: {e}")
        return JSONResponse(
            status_code=500,
            content={"status": "error", "message": str(e)}
        )

# ... (sisa kode main.py lainnya tetap sama)

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "bot": "Guru Assistant Bot",
        "version": "1.0.0"
    }

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Guru Assistant Bot is running!",
        "webhook": "/webhook",
        "health": "/health"
    }

async def on_startup():
    """Setup saat app mulai"""
    from bot import set_commands
    await set_commands()
    logger.info("Bot started successfully")

async def on_shutdown():
    """Cleanup saat app berhenti"""
    await bot.session.close()
    logger.info("Bot stopped")

app.add_event_handler("startup", on_startup)
app.add_event_handler("shutdown", on_shutdown)

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=port,
        reload=True  # Set False di production
    )
