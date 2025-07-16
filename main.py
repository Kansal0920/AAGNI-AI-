import logging
import os
import asyncio
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters
from google.generativeai import configure, GenerativeModel
from gtts import gTTS
import uuid
from datetime import datetime
import nest_asyncio

# 🧠 Voice playback is skipped on Render (no audio devices)
IS_RENDER = os.environ.get("RENDER", "false").lower() == "true"

# 📋 Logging
logging.basicConfig(
    format='%(asctime)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# 📌 Config
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

# 🧠 Configure Gemini Flash model
configure(api_key=GEMINI_API_KEY)
gemini = GenerativeModel("models/gemini-1.5-flash")

# ✅ Main logic to generate AI response
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_msg = update.message.text
    user_name = update.effective_user.first_name or "User"
    chat_id = update.effective_chat.id

    logging.info(f"Message from {chat_id}: {user_msg}")

    try:
        response = gemini.generate_content(user_msg)
        bot_reply = response.text.strip()
    except Exception as e:
        bot_reply = "❌ Gemini API error: I'm currently unavailable."
        logging.error(f"Gemini API error: {e}")

    # 🗣️ Send text reply
    await context.bot.send_message(chat_id=chat_id, text=bot_reply)

    # 🎙️ Convert text to voice (saved as .mp3)
    filename = f"voice_{uuid.uuid4()}.mp3"
    tts = gTTS(bot_reply, lang='en')
    tts.save(filename)

    # 🧠 Skip playback on Render
    if not IS_RENDER:
        try:
            import pygame
            pygame.mixer.init()
            pygame.mixer.music.load(filename)
            pygame.mixer.music.play()
            while pygame.mixer.music.get_busy():
                continue
        except Exception as e:
            logging.warning(f"🎵 Voice playback failed: {e}")
    else:
        logging.info(f"🖥️ Render detected: Skipping audio playback. Voice file: {filename}")

# 🛠️ Start bot
async def main():
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
    logging.info("🤖 AAGNI bot started...")
    await app.run_polling()

# ✅ Run
nest_asyncio.apply()
asyncio.get_event_loop().run_until_complete(main())
