import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# ---------------- Настройки ----------------
TOKEN = "7335593108:AAHjyiXOA8wBRxaVRx_3VobA91DXZCjjQRM"
ADMIN_CHAT_ID = 7371605868

# Настройка Google Sheets
scope = ["https://spreadsheets.google.com/feeds",
         "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
client = gspread.authorize(creds)
sheet = client.open("TestBotData").sheet1  # имя таблицы

# ---------------- Инициализация бота ----------------
bot = Bot(token=TOKEN)
dp = Dispatcher()

# ---------------- Хранилище данных пользователей ----------------
user_data = {}

# ---------------- Команда /start ----------------
@dp.message(Command("start"))
async def start(message: types.Message):
    user_data[message.from_user.id] = {}
    await message.answer("Привет! Давай начнём тест.\nБыл ли у вас опыт в данной сфере? (Да/Нет)")

# ---------------- Обработка ответов ----------------
@dp.message()
async def process_test(message: types.Message):
    user_id = message.from_user.id
    data = user_data.get(user_id, {})

    # Вопрос 1: опыт
    if "experience" not in data:
        data["experience"] = message.text
        user_data[user_id] = data
        await message.answer("Какие у вас были профиты/достижения? Напишите текстом.")
        return

    # Вопрос 2: профиты
    if "profits" not in data:
        data["profits"] = message.text
        user_data[user_id] = data
        await message.answer("На сколько времени вы планируете быть в команде? (<1 мес / 1–3 мес / 3–6 мес / >6 мес)")
        return

    # Вопрос 3: длительность
    if "duration" not in data:
        data["duration"] = message.text
        user_data[user_id] = data

        # ---------------- Сохраняем в Google Sheets ----------------
        sheet.append_row([message.from_user.id, data["experience"], data["profits"], data["duration"]])

        # ---------------- Отправляем уведомление админу ----------------
        await bot.send_message(ADMIN_CHAT_ID,
                               f"Новый кандидат!\n"
                               f"ID: {message.from_user.id}\n"
                               f"Опыт: {data['experience']}\n"
                               f"Профиты: {data['profits']}\n"
                               f"Длительность: {data['duration']}")

        await message.answer("Спасибо! Тест завершён. Скоро с вами свяжутся.")
        del user_data[user_id]

# ---------------- Запуск бота ----------------
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
