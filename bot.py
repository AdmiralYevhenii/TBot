from flask import Flask, request
from telegram import Bot
import os
import random
import time
import json
import openai
import asyncio

# Токен бота
TOKEN = "8029573466:AAFq4B_d-s73bPG0z9kRcOAU2sE3wFwAsj4"
WEBHOOK_URL = "https://tbot-pexl.onrender.com"  # URL на Render
BOT_USERNAME = "PidpuvasBot"  # Ім'я бота

# Ініціалізація OpenAI
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise ValueError("Не знайдено OpenAI API ключ у змінних оточення.")
openai.api_key = OPENAI_API_KEY

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

# Функція для відправки повідомлення
async def send_message(chat_id, text, message_id=None):

    #Асинхронна функція для відправки повідомлення як відповідь.

    bot = Bot(token=TOKEN)
    await bot.send_message(chat_id=chat_id, text=text, reply_to_message_id=message_id)

# Функція для генерації відповіді OpenAI
def get_openai_response(prompt):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",  # або "gpt-3.5-turbo"
            messages=[
                {"role": "system", "content": "Ти є корисним помічником."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=150
        )
        return response['choices'][0]['message']['content'].strip()
    except Exception as e:
        return f"Помилка: {str(e)}"

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

        # Логування отриманого тексту
        print(f"Received message: {text}")

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
            send_message(chat_id, f"{username}, сходи попісяй", message_id)
            user_char_count[username] = 0

        # Ігнорування команд, адресованих іншому боту
        if "@" in text:
             if BOT_USERNAME not in text:
                return "OK", 200  # Ігноруємо команду, якщо вона для іншого бота

        # Перевірка на команду
        if text.startswith("/"):
            # Логування команди
            print(f"Command received: {text}")

            # Команда /whoiam
            if text.lower().startswith("/whoiam"):
                random_response = random.choice(responses).strip()
                send_message(chat_id, f"{random_response}", message_id)

            # Команда /help
            elif text.lower().startswith("/help"):
                help_text = (
                    "Команди бота:\n"
                    "/whoiam - Дізнайся хто ти\n"
                    "/shishka - Показати всім розмір твоєї шишки\n"
                    "/cocktail - Отримати випадковий коктейль\n"
                    "/ask - Задати питання AI"
                )
                send_message(chat_id, help_text, message_id)

            # Команда /shishka
            elif text.lower().startswith("/shishka"):
                shishka_response = generate_shishka()
                send_message(chat_id, f"{shishka_response}", message_id)

            # Команда /cocktail
            elif text.lower().startswith("/cocktail"):
                cocktails = load_cocktails()
                cocktail = random.choice(cocktails)
                ingredients = "\n".join(cocktail["ingredients"])
                preparation = cocktail["preparation"]
                cocktail_response = (
                    f"Коктейль: {cocktail['name']}\n"
                    f"Складові:\n{ingredients}\n"
                    f"Як приготувати:\n{preparation}"
                )
                send_message(chat_id, cocktail_response, message_id)

            # Команда /ask
            elif text.lower().startswith("/ask"):
                prompt = text[len("/ask"):].strip()
                if not prompt:  # Якщо запит пустий
                    send_message(chat_id, "Будь ласка, напишіть запит після команди /ask.", message_id)
                else:
                    response = get_openai_response(prompt)
                    send_message(chat_id, response, message_id)

    return "OK", 200


if __name__ == "__main__":
    bot = Bot(token=TOKEN)
    bot.set_webhook(url=f"{WEBHOOK_URL}/{TOKEN}")
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
