from telethon import TelegramClient, events
from telethon.sessions import StringSession
import aiohttp
import asyncio
from langdetect import detect
from datetime import datetime, time
import os

# Environment Variables (recommended for Vercel)
API_ID = int(os.environ['API_ID'])
API_HASH = os.environ['API_HASH']
SESSION_STRING = os.environ['SESSION_STRING']
OPENROUTER_API_KEY = os.environ['OPENROUTER_API_KEY']

# Initialize Telegram client
client = TelegramClient(StringSession(SESSION_STRING), API_ID, API_HASH)

# School schedule
SCHOOL_START = time(8, 30)
SCHOOL_END = time(17, 30)
WEEKDAYS = [0, 1, 2, 3, 4]  # Monday to Friday

# Helper Functions
def is_school_time():
    now = datetime.now()
    return now.weekday() in WEEKDAYS and SCHOOL_START <= now.time() <= SCHOOL_END

async def simulate_typing(event):
    async with client.action(event.chat_id, 'typing'):
        await asyncio.sleep(2)

async def generate_ai_response(prompt, language):
    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
    }
    if language == 'uz':
        system_message = "Siz o'zbek yigitisi sifatida javob berasiz. Tabiiy va odatiy tarzda gapling."
    elif language == 'ru':
        system_message = "Вы отвечаете как обычный парень. Говорите естественно и по-человечески."
    else:
        system_message = "You respond as a friendly guy. Keep it natural and human-like."

    data = {
        "model": "gpt-3.5-turbo",
        "messages": [
            {"role": "system", "content": system_message},
            {"role": "user", "content": prompt},
        ],
        "max_tokens": 150,
    }

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, json=data) as response:
                result = await response.json()
                return result['choices'][0]['message']['content'].strip()
    except Exception:
        return "Oops, something went wrong. Let's talk about something else!"

# Telegram event handler
@client.on(events.NewMessage(incoming=True))
async def handle_message(event):
    await event.message.mark_read()
    sender = await event.get_sender()
    message_text = event.message.message
    print(f"Received message from {sender.username}: {message_text}")

    if is_school_time():
        await event.reply("Hozir maktabdaman, keyinroq gaplashamiz!")
        return

    try:
        language = detect(message_text)
    except:
        language = 'uz'

    if language not in ['uz', 'ru', 'en']:
        language = 'uz'

    await simulate_typing(event)
    ai_response = await generate_ai_response(message_text, language)
    await event.reply(ai_response)

# Vercel handler
async def handler(request):
    await client.connect()
    if not await client.is_user_authorized():
        await client.disconnect()
        return {
            "statusCode": 401,
            "body": "Unauthorized",
        }
    await client.run_until_disconnected()
    return {
        "statusCode": 200,
        "body": "Telegram Bot Running",
    }

# For Vercel Python API
async def main(request, response):
    return await handler(request)
