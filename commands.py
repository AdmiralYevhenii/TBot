import random
import json
from telegram import Bot

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

# Читання списку відповідей з файлу
def load_responses():
    with open("responses.txt", "r", encoding="utf-8") as file:
        return file.readlines()

responses = load_responses()

# Завантаження коктейлів
def load_cocktails():
    with open("cocktails.json", "r", encoding="utf-8") as file:
        return json.load(file)

# Обробка команди /whoiam
def handle_whoiam(chat_id, bot):
    random_response = random.choice(responses).strip()
    bot.send_message(chat_id, random_response)

# Обробка команди /shishka
def handle_shishka(chat_id, bot):
    shishka_response = generate_shishka()
    bot.send_message(chat_id, shishka_response)

# Обробка команди /cocktail
def handle_cocktail(chat_id, bot):
    cocktails = load_cocktails()
    cocktail = random.choice(cocktails)
    ingredients = "\n".join(cocktail["ingredients"])
    preparation = cocktail["preparation"]
    cocktail_response = (
        f"Коктейль: {cocktail['name']}\n"
        f"Складові:\n{ingredients}\n"
        f"Як приготувати:\n{preparation}"
    )
    bot.send_message(chat_id, cocktail_response)

# Обробка команди /help
def handle_help(chat_id, bot):
    help_text = (
        "Команди бота:\n"
        "/whoiam - Дізнайся хто ти\n"
        "/shishka - Показати всім розмір твоєї шишки\n"
        "/cocktail - Отримати випадковий коктейль"
    )
    bot.send_message(chat_id, help_text)
