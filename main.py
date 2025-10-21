import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from flask import Flask
from threading import Thread

# ---------------- Настройки бота ----------------
TOKEN = "7335593108:AAHjyiXOA8wBRxaVRx_3VobA91DXZCjjQRM"
ADMIN_CHAT_ID = 7371605868

# ---------------- Настройка Google Sheets ----------------
scope = ["https://spreadsheets.google.com/feeds",
         "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
client = gspread.authorize(creds)
sheet = client.open("TestBotData").sheet1  # Имя таблицы

# ---------------- Инициализация бота ----------------
bot = Bot(token=TOKEN)
dp = Dispatcher()

# ---------------- Хранилище данных пользователей ----------------
user_data = {}

# ---------------- Веб-сервер для 24/7 ----------------
app = Flask('')

@app.route('/')
def home():
    return "Bot is running"

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run)
    t.start()

# ---------------- Команда /start ----------------
@dp.message(Command("start"))
async def start(message: types.Message):
    username = message.from_user.username
    if not username:
        await message.answer("У вас нет @username, пожалуйста, добавьте его в Telegram, чтобы пройти тест.")
        return

    user_data[username] = {}
    await message.answer("Привет! Давай начнём тест.\nБыл ли у вас опыт в данной сфере? (Да/Нет)")

# ---------------- Обработка ответов ----------------
@dp.message()
async def process_test(message: types.Message):
    username = message.from_user.username
    if not username:
        await message.answer("У вас нет @username, невозможно сохранить данные.")
        return

    data = user_data.get(username, {})

    # Вопрос 1: опыт
    if "experience" not in data:
        data["experience"] = message.text
        user_data[username] = data
        await message.answer("Какие у вас были профиты/достижения? Напишите текстом.")
        return

    # Вопрос 2: профиты
    if "profits" not in data:
        data["profits"] = message.text
        user_data[username] = data
        await message.answer("На сколько времени вы планируете быть в команде? (<1 мес / 1–3 мес / 3–6 мес / >6 мес)")
        return

    # Вопрос 3: длительность
    if "duration" not in data:
        data["duration"] = message.text
        user_data[username] = data

        # ---------------- Сохраняем в Google Sheets ----------------
        sheet.append_row([username, data["experience"], data["profits"], data["duration"]])

        # ---------------- Отправляем уведомление админу ----------------
        await bot.send_message(ADMIN_CHAT_ID,
                               f"Новый кандидат!\n"
                               f"@{username}\n"
                               f"Опыт: {data['experience']}\n"
                               f"Профиты: {data['profits']}\n"
                               f"Длительность: {data['duration']}")

        await message.answer("Спасибо! Тест завершён. Скоро с вами свяжутся.")
        del user_data[username]

# ---------------- Запуск бота ----------------
async def main():
    await dp.start_polling(bot)

# ---------------- Старт веб-сервера и бота ----------------
keep_alive()
asyncio.run(main())
