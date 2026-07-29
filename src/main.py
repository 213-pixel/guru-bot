from fastapi import FastAPI, Request, Response
from fastapi.responses import JSONResponse
from aiogram.types import Update
import uvicorn
import os
from dotenv import load_dotenv
from src.bot import bot, dp
from src.utils.logger import logger

load_dotenv()

app = FastAPI(
    title="Guru Assistant Bot API",
    description="Telegram Bot untuk membantu administrasi guru",
    version="1.0.0"
)

@app.post("/webhook")
async def webhook(request: Request):
    """
    Endpoint untuk menerima update dari Telegram
    """
    try:
        # Parse request body
        body = await request.json()
        
        # Convert ke Update object
        update = Update.model_validate(body, context={"bot": bot})
        
        # Feed ke dispatcher
        await dp.feed_update(bot, update)
        
        return JSONResponse(content={"status": "ok"})
        
    except Exception as e:
        logger.error(f"Webhook error: {e}")
        return JSONResponse(
            status_code=500,
            content={"status": "error", "message": str(e)}
        )

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
    from src.bot import set_commands
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
        "src.main:app",
        host="0.0.0.0",
        port=port,
        reload=True  # Set False di production
    )