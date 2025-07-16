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

# Try initializing pygame safely (some cloud platforms don’t support audio)
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

# Dynamic Personality
def detect_mode(text):
    if "jai shree ram" in text.lower():
        return "devotional"
    elif "bro" in text.lower() or "hi" in text.lower():
        return "friendly"
    else:
        return "formal"

def format_response(reply, mode):
    if mode == "devotional":
        return f"🚩 Jai Shree Ram Bhakt 🙏\n\n{reply}"
    elif mode == "friendly":
        return f"😎 Bro here's the reply:\n\n{reply}"
    else:
        return f"🤖 AAGNI says:\n\n{reply}"

# Message Handler
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text
    user_id = update.message.from_user.id
    logging.info(f"Message from {user_id}: {user_message}")

    mode = detect_mode(user_message)

    try:
        gemini_response = model.generate_content(user_message).text
    except Exception as e:
        logging.error(f"Gemini API error: {e}")
        gemini_response = "❌ Sorry, there was an error generating a response."

    final_reply = format_response(gemini_response, mode)
    await update.message.reply_text(final_reply)

    # Voice Output (optional in cloud)
    try:
        speak_text(gemini_response)
    except Exception as e:
        logging.warning(f"Voice failed: {e}")

# Main function
async def main():
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
    logging.info("🤖 AAGNI bot started and polling...")
    await app.run_polling()

# Entry
if __name__ == "__main__":
    nest_asyncio.apply()
    asyncio.get_event_loop().run_until_complete(main())
