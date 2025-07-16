import os
import logging
import asyncio
import nest_asyncio
from gtts import gTTS
import pygame
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables
if os.getenv("RENDER") is None:
    load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Logger
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Enable asyncio fix for nested event loops (needed for Render)
nest_asyncio.apply()

# Configure Gemini API
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("models/gemini-1.5-flash-latest")

# Initialize pygame mixer without crashing on Render
try:
    pygame.mixer.init()
except pygame.error:
    logging.warning("🎵 Audio playback not supported on this platform")

# Voice output function
def speak(text: str):
    tts = gTTS(text=text, lang='en')
    filename = "aagni_voice.mp3"
    tts.save(filename)
    try:
        pygame.mixer.music.load(filename)
        pygame.mixer.music.play()
    except pygame.error:
        logging.warning("🎵 Unable to play audio on this platform")

# Personality Engine
def get_personality_mode(message: str):
    msg = message.lower()
    if "jai shree ram" in msg or "hare krishna" in msg:
        return "devotional"
    elif "hi" in msg or "hello" in msg:
        return "casual"
    else:
        return "default"

def stylize_reply(reply, mode):
    if mode == "devotional":
        return f"🙏 Jai Shree Ram! AAGNI says: {reply}"
    elif mode == "casual":
        return f"😄 Heyyy buddy! You said: {reply}"
    else:
        return f"AAGNI 🤖: {reply}"

# Gemini Response
async def get_gemini_reply(message: str) -> str:
    try:
        response = model.generate_content(message)
        return response.text.strip()
    except Exception as e:
        logging.error(f"Gemini API error: {e}")
        return "⚠️ Sorry, AAGNI is facing some issue right now."

# Handler
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_msg = update.message.text
    user_id = update.effective_user.id
    logging.info(f"Message from {user_id}: {user_msg}")

    mode = get_personality_mode(user_msg)
    reply_text = await get_gemini_reply(user_msg)
    final_reply = stylize_reply(reply_text, mode)

    await update.message.reply_text(final_reply)
    speak(reply_text)

# Main function
async def main():
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    logging.info("🤖 AAGNI bot started...")
    await app.run_polling()

if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(main())
