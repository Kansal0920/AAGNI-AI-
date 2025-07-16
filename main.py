import os
import asyncio
import logging
import nest_asyncio
from dotenv import load_dotenv
from gtts import gTTS
import pygame

from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

from google.generativeai import GenerativeModel, configure

# ✅ Load env variables
load_dotenv()
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# ✅ Configure Gemini
configure(api_key=GEMINI_API_KEY)
model = GenerativeModel("models/gemini-1.5-flash")

# ✅ Setup logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# ✅ Voice init
try:
    pygame.mixer.init()
    VOICE_ENABLED = True
except pygame.error:
    VOICE_ENABLED = False
    logging.warning("🎵 Audio playback not supported on this platform")

# ✅ Start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🔥 AAGNI at your service, Sir!")

# ✅ Handle messages
async def reply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.message.text
    user_id = update.message.from_user.id
    logging.info(f"Message from {user_id}: {msg}")

    try:
        gemini_reply = model.generate_content(msg).text
    except Exception as e:
        gemini_reply = "⚠️ Gemini API error. Try again later."
        logging.error(f"Gemini API error: {e}")

    await update.message.reply_text(gemini_reply)

    # 🎙️ Voice reply if local
    if VOICE_ENABLED:
        try:
            tts = gTTS(text=gemini_reply, lang="en")
            tts.save("voice.mp3")
            pygame.mixer.music.load("voice.mp3")
            pygame.mixer.music.play()
        except Exception as e:
            logging.warning(f"Voice failed: {e}")

# ✅ Main async function
async def main():
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, reply))

    logging.info("🤖 AAGNI bot started...")
    await app.run_polling()

# ✅ Run app
nest_asyncio.apply()
asyncio.get_event_loop().run_until_complete(main())
