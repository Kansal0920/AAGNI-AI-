import os
import asyncio
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, ContextTypes, filters
from google.generativeai import GenerativeModel, configure
from gtts import gTTS
import pygame
from dotenv import load_dotenv


load_dotenv()
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")


configure(api_key=GEMINI_API_KEY)
model = GenerativeModel("models/gemini-1.5-flash")


try:
    pygame.mixer.init()
except:
    print("⚠️ Audio not supported on this platform")


def speak(text):
    tts = gTTS(text=text, lang='en')
    tts.save("voice.mp3")
    try:
        pygame.mixer.music.load("voice.mp3")
        pygame.mixer.music.play()
    except:
        print("⚠️ Unable to play audio")



def get_mode(text):
    if "jai shree ram" in text.lower():
        return "devotional"
    elif "hi" in text.lower() or "bro" in text.lower():
        return "friendly"
    else:
        return "formal"


def format_reply(text, mode):
    if mode == "devotional":
        return "🚩 Jai Shree Ram Bhakt 🙏\n\n" + text
    elif mode == "friendly":
        return "😎 Bro here's the reply:\n\n" + text
    else:
        return "🤖 AAGNI says:\n\n" + text


async def reply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text
    mode = get_mode(user_message)

    # Gemini response
    response = model.generate_content(user_message)
    reply_text = response.text

    # Format and reply
    final_msg = format_reply(reply_text, mode)
    await update.message.reply_text(final_msg)
    speak(reply_text)  # speak only raw reply


async def main():
    print("🤖 AAGNI is now running...")
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, reply))
    await app.run_polling()
    
if __name__ == "__main__":
    print("🤖 AAGNI is now running...")
    import nest_asyncio
    nest_asyncio.apply()
    asyncio.get_event_loop().run_until_complete(main())

