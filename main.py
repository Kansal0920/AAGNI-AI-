import os
import logging
import asyncio
import requests
import tempfile
import nest_asyncio
from telegram import Update, InputFile
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, CommandHandler, filters
from gtts import gTTS
import pygame
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Voice initialization
pygame.mixer.init()

# Fix event loop crash issue (Jupyter/macOS)
nest_asyncio.apply()

# ✨ Personality Engine
def get_personality_mode(text: str):
    text = text.lower()
    if "jai shree ram" in text:
        return "devotional"
    elif "hi" in text or "hello" in text:
        return "friendly"
    elif "aagni" in text or "start" in text:
        return "formal"
    return "neutral"

# 🎤 Speak in male voice using gTTS
def speak_text(text: str):
    tts = gTTS(text, lang="en")
    with tempfile.NamedTemporaryFile(delete=True, suffix=".mp3") as fp:
        tts.save(fp.name)
        pygame.mixer.music.load(fp.name)
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy():
            continue

# 🤖 Gemini API call (Flash Free Model)
def query_gemini(prompt: str) -> str:
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
    headers = {"Content-Type": "application/json"}
    data = {"contents": [{"parts": [{"text": prompt}]}]}
    try:
        res = requests.post(url, headers=headers, json=data)
        res.raise_for_status()
        return res.json()["candidates"][0]["content"]["parts"][0]["text"]
    except Exception as e:
        logger.error(f"Gemini API error: {e}")
        return "⚠️ Sorry, AAGNI couldn't fetch a reply."

# 📁 File handler
async def handle_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    file = update.message.document or update.message.photo[-1] if update.message.photo else None
    if not file:
        return await update.message.reply_text("No file detected.")
    file_id = file.file_id
    telegram_file = await context.bot.get_file(file_id)
    file_path = f"received_{file.file_unique_id}"
    await telegram_file.download_to_drive(file_path)
    await update.message.reply_text(f"📥 File received: {file_path}")

# 💬 Main message handler
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text
    username = update.effective_user.username or update.effective_user.first_name
    logger.info(f"Message from {username}: {user_text}")

    mode = get_personality_mode(user_text)
    prefix = {
        "friendly": "😄 Heyyy buddy! ",
        "devotional": "🙏 Jai Shree Ram! ",
        "formal": "🤖 Hello respected developer. ",
        "neutral": "👋 "
    }.get(mode, "👋 ")

    reply = query_gemini(user_text)
    full_reply = prefix + reply
    await update.message.reply_text(full_reply)

    try:
        speak_text(reply)
    except Exception as e:
        logger.warning(f"Voice output error: {e}")

# 🟢 Start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 Hello! AAGNI is ready to serve you!")

# 🚀 App runner
async def main():
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
    app.add_handler(MessageHandler(filters.Document.ALL | filters.PHOTO, handle_file))
    logger.info("🤖 AAGNI bot started...")
    await app.run_polling()

if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(main())
