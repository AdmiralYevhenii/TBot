import random
import time
import asyncio
import json
from flask import Flask, request
from telegram import Bot
import os
import openai

# Токен бота
TOKEN = "8029573466:AAFq4B_d-s73bPG0z9kRcOAU2sE3wFwAsj4"
WEBHOOK_URL = "https://tbot-pexl.onrender.com"  # URL на Render

openai.api_key = os.getenv("OPENAI_API_KEY")  # Отримання ключа API з середовища


app = Flask(__name__)

# Зберігаємо статистику користувачів: кількість символів та час останнього повідомлення
user_char_count = {}
user_last_message_time = {}

# Читання списку відповідей з файлу
def load_responses():
    with open("responses.txt", "r", encoding="utf-8") as file:
        return file.readlines()

responses = load_responses()

# Читання списку коктейлів з файлу
def load_cocktails():
    with open("cocktails.json", "r", encoding="utf-8") as file:
        return json.load(file)

async def send_message(chat_id, text, message_id=None):
    """Асинхронна функція для відправки повідомлення як відповідь."""
    bot = Bot(token=TOKEN)
    await bot.send_message(chat_id=chat_id, text=text, reply_to_message_id=message_id)

async def get_gpt_response(prompt):
    """Отримати відповідь від GPT-3 за допомогою OpenAI API."""
    response = openai.Completion.create(
        engine="text-davinci-003",
        prompt=prompt,
        max_tokens=150,  # Максимальна кількість токенів для відповіді
        temperature=0.7,  # Впливає на креативність відповіді
    )
    return response.choices[0].text.strip()

# Функція для генерації шишки
def generate_shishka():
    random_choice = random.choices(
        [random.randint(5, 15), random.randint(15, 20), random.randint(20, 25), random.randint(25, 30), 1], 
        weights=[50, 25, 10, 5, 1], k=1
    )[0]
    
    if 5 <= random_choice <= 15:
        return f"Твоя шишка {random_choice} см"
    elif 15 < random_choice <= 20:
        return f"Твоя шишка {random_choice} см"
    elif 20 < random_choice <= 25:
        return f"Твоя шишка {random_choice} см"
    elif 25 < random_choice <= 30:
        return f"Твоя шишка {random_choice} см"
    else:
        return f"Твоя шишка {random_choice} см, їбать ти лох"

@app.route(f"/{TOKEN}", methods=["POST"])
def webhook():
    update = request.get_json()

    if "message" in update:
        chat_id = update["message"]["chat"]["id"]
        message_id = update["message"]["message_id"]  # ID повідомлення для відповіді
        username = update["message"]["from"]["first_name"]
        text = update["message"].get("text", "")
        message_time = time.time()

        # Оновлюємо кількість символів для користувача
        if username not in user_char_count:
            user_char_count[username] = 0
            user_last_message_time[username] = message_time

        if message_time - user_last_message_time[username] > 600:
            user_char_count[username] = 0

        user_char_count[username] += len(text)
        user_last_message_time[username] = message_time

        # Перевірка на 800 символів
        if user_char_count[username] >= 800:
            asyncio.ensure_future(send_message(chat_id, f"{username}, сходи попісяй", message_id))
            user_char_count[username] = 0

        # Обробка команд
        if text.startswith("/"):
            if text.lower() == "/whoiam":
                random_response = random.choice(responses).strip()
                asyncio.ensure_future(send_message(chat_id, random_response, message_id))
            elif text.lower() == "/help":
                help_text = (
                    "Команди бота:\n"
                    "/whoiam - Дізнайся хто ти\n"
                    "/bump - Показати всім розмір твоєї шишки\n"
                    "/cocktail - Отримати випадковий коктейль"
                )
                asyncio.ensure_future(send_message(chat_id, help_text, message_id))
            elif text.lower() == "/bump":
                shishka_response = generate_shishka()
                asyncio.ensure_future(send_message(chat_id, shishka_response, message_id))
            elif text.lower() == "/cocktail":
                cocktails = load_cocktails()
                cocktail = random.choice(cocktails)
                ingredients = "\n".join(cocktail["ingredients"])
                preparation = cocktail["preparation"]
                cocktail_response = (
                    f"Коктейль: {cocktail['name']}\n"
                    f"Складові:\n{ingredients}\n"
                    f"Як приготувати:\n{preparation}"
                )
                asyncio.ensure_future(send_message(chat_id, cocktail_response, message_id))
            else:
                asyncio.ensure_future(send_message(chat_id, "Невідома команда. Використовуйте '/help' для допомоги.", message_id))
        else:
            # Визначаємо випадковий шанс для GPT включитися в бесіду
            if random.random() < 0.05:  # 5% шанс на GPT відповідь
                gpt_response = asyncio.run(get_gpt_response(text))  # Отримуємо відповідь від GPT
                asyncio.ensure_future(send_message(chat_id, gpt_response, message_id))
            else:
                asyncio.ensure_future(send_message(chat_id, "Я вас чую! Продовжуємо розмову.", message_id))

    return "OK", 200

if __name__ == "__main__":
    bot = Bot(token=TOKEN)
    bot.set_webhook(url=f"{WEBHOOK_URL}/{TOKEN}")
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
