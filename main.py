import os
import pygame
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, ContextTypes, filters
from dotenv import load_dotenv
import requests
from gtts import gTTS

# Load environment variables
load_dotenv()
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
MODEL = "openai/gpt-3.5-turbo"

# Setup Pygame for voice output
pygame.init()
pygame.mixer.init()

def speak(text):
    tts = gTTS(text=text, lang='en')
    tts.save("voice.mp3")
    pygame.mixer.music.load("voice.mp3")
    pygame.mixer.music.play()
    while pygame.mixer.music.get_busy():
        continue

# Send message to OpenRouter
def chat_with_openrouter(message):
    try:
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": MODEL,
                "messages": [
                    {"role": "system", "content": "You are AAGNI, a powerful AI assistant like Jarvis."},
                    {"role": "user", "content": message}
                ]
            }
        )

        data = response.json()

        # Handle possible errors
        if "choices" not in data:
            return "❌ AI server not responding."

        return data["choices"][0]["message"]["content"]

    except Exception as e:
        return f"❌ AI error: {str(e)}"

# Telegram bot handler
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text
    ai_response = chat_with_openrouter(user_message)
    await update.message.reply_text(ai_response)
    speak(ai_response)

# Run the bot
def main():
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    print("✅ AAGNI is live and ready to chat!")
    app.run_polling()

if __name__ == "__main__":
    main()
