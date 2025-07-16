import os
import asyncio
import nest_asyncio
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters
from google.generativeai import GenerativeModel, configure
from gtts import gTTS
import pygame
import logging

# Setup Logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Load environment variables
load_dotenv()
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Configure Gemini
configure(api_key=GEMINI_API_KEY)
model = GenerativeModel("models/gemini-1.5-flash")

# Initialize Pygame (skip audio on unsupported platforms)
try:
    pygame.mixer.init()
except Exception:
    logging.warning("🎵 Audio playback not supported on this platform")

# Voice Function
def speak_text(text, filename="output.mp3"):
    tts = gTTS(text=text, lang='en')
    tts.save(filename)
    try:
        pygame.mixer.music.load(filename)
        pygame.mixer.music.play()
    except Exception:
        logging.warning("🎵 Cannot play audio. Skipping...")

# Detect personality mode
def detect_mode(text):
    if "jai shree ram" in text.lower():
        return "devotional"
    elif "bro" in text.lower() or "hi" in text.lower():
        return "friendly"
    else:
        return "formal"

# Format reply based on mode
def format_response(reply, mode):
    if mode == "devotional":
        return f"🚩 Jai Shree Ram Bhakt 🙏\n\n{reply}"
    elif mode == "friendly":
        return f"😎 Bro here's the reply:\n\n{reply}"
    else:
        return f"🤖 AAGNI says:\n\n{reply}"

# Handle incoming messages
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_msg = update.message.text
    mode = detect_mode(user_msg)
    
    try:
        gemini_reply = model.generate_content(user_msg).text
        final_reply = format_response(gemini_reply, mode)
        await update.message.reply_text(final_reply)
        speak_text(gemini_reply)
        logging.info(f"✅ Responded to: {user_msg}")
    except Exception as e:
        error_msg = f"❌ Gemini API error: {e}"
        logging.error(error_msg)
        await update.message.reply_text("⚠️ Sorry, something went wrong. Please try again later.")

# Main Bot Application
async def main():
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    logging.info("🤖 AAGNI is now running 24x7...")
    await app.run_polling()

# Run safely with nested asyncio
if __name__ == "__main__":
    nest_asyncio.apply()
    asyncio.get_event_loop().run_until_complete(main())
