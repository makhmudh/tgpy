from telethon import TelegramClient, events
from telethon.sessions import StringSession
import aiohttp  # For asynchronous HTTP requests
import asyncio
from langdetect import detect  # For language detection
from datetime import datetime, time  # For schedule handling

# Replace these with your own values
API_ID = '11862100'  # Get from https://my.telegram.org
API_HASH = '6b86628d4a2b1b984e5c652894a45018'  # Get from https://my.telegram.org
SESSION_STRING = '1ApWapzMBuyCl70tR5djQ9QRRW7OqQE-gWJOswKgsfZRRBbP0BnUca1cZB-_XqtmZBxL4Jk8lqkFdLCWSW6IwPUCnLk9XA1zo2lYNr81hdcYAv5VN2mgWZIyWDszdKIk78RaksSBKguZtK0177TJfeBceuOZ7Hv63lbBkirowXkf7V8IafhUnf6fRpnw03h8ZONZCR2b5jc3X8MLVwBy1r6hMlHKt6JUr4KL8wVXNjeZdOzI4YxSTMrFpH4lGSUNCWS4S4t9HCRwxE35feN1m9kMhBxBzskviovGZlHI48vse6fSpd8FmaQGt7Ic9UzwABPpbRP0U9ggQIyEA64L9LLLJpkPMkO0='  # Generated using Telethon
OPENROUTER_API_KEY = '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'  # Get from https://openrouter.ai/

# Initialize Telegram client
client = TelegramClient(StringSession(SESSION_STRING), API_ID, API_HASH)

# School schedule (8:30–17:30, Monday to Friday)
SCHOOL_START = time(8, 30)
SCHOOL_END = time(17, 30)
WEEKDAYS = [0, 1, 2, 3, 4]  # Monday to Friday

# Function to check if it's school time
def is_school_time():
    now = datetime.now()
    return now.weekday() in WEEKDAYS and SCHOOL_START <= now.time() <= SCHOOL_END

# Function to simulate human typing
async def simulate_typing(event):
    async with client.action(event.chat_id, 'typing'):
        await asyncio.sleep(2)  # Simulate typing for 2 seconds

# Function to generate AI response using OpenRouter's GPT-3.5
async def generate_ai_response(prompt, language):
    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
    }

    # Set the system message based on the detected language
    if language == 'uz':
        system_message = "Siz o'zbek yigitisi sifatida javob berasiz. Tabiiy va odatiy tarzda gapling."
    elif language == 'ru':
        system_message = "Вы отвечаете как обычный парень. Говорите естественно и по-человечески."
    else:
        system_message = "You respond as a friendly guy. Keep it natural and human-like."

    data = {
        "model": "gpt-3.5-turbo",  # Use GPT-3.5-turbo via OpenRouter
        "messages": [
            {"role": "system", "content": system_message},
            {"role": "user", "content": prompt},
        ],
        "max_tokens": 150,  # Limit response length
    }

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, json=data) as response:
                result = await response.json()
                return result['choices'][0]['message']['content'].strip()
    except Exception as e:
        return f"Oops, something went wrong. Let's talk about something else!"

# Event handler for incoming messages
@client.on(events.NewMessage(incoming=True))
async def handle_message(event):
    # Mark the message as read (✓✓)
    await event.message.mark_read()

    sender = await event.get_sender()
    message_text = event.message.message

    print(f"Received message from {sender.username}: {message_text}")

    # Check if it's school time
    if is_school_time():
        await event.reply("Hozir maktabdaman, keyinroq gaplashamiz!")
        return

    # Detect the language of the incoming message
    try:
        language = detect(message_text)
    except:
        language = 'uz'  # Default to Uzbek if detection fails

    # Map detected language to a specific language code
    if language in ['uz', 'ru', 'en']:
        pass  # Keep as is
    else:
        language = 'uz'  # Default to Uzbek for other languages

    # Simulate human typing
    await simulate_typing(event)

    # Generate AI response
    ai_response = await generate_ai_response(message_text, language)
    await event.reply(ai_response)

# Function to keep the account online
async def keep_online():
    while True:
        try:
            # Send a small request to keep the account online
            await client.get_me()
            print("Still online...")
            await asyncio.sleep(60)  # Wait for 60 seconds before the next request
        except Exception as e:
            print(f"Error: {e}. Retrying in 10 seconds...")
            await asyncio.sleep(10)
            # Start the client
async def main():
    await client.start()
    print("Telegram AI bot is running...")

    # Run the "always online" function in the background
    asyncio.create_task(keep_online())

    # Keep the bot running
    await client.run_until_disconnected()

# Run the script
if __name__ == "__main__":
    asyncio.run(main()) 
SCHOOL_END = time(17, 30)
WEEKDAYS = [0, 1, 2, 3, 4]  # Monday to Friday
