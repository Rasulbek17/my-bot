from aiogram import Bot, Dispatcher, types, F
from aiogram.enums import ParseMode
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, Message
from aiogram.client.default import DefaultBotProperties
import asyncio
from config import BOT_TOKEN, ADMIN_ID

bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()
user_data = {}

@dp.message(F.text == "/start")
async def start_handler(message: Message):
    await message.answer("Атыңызды жазыңыз:")
    user_data[message.from_user.id] = {"step": "name"}

@dp.message(F.text)
async def handle_text(message: Message):
    user_id = message.from_user.id
    if user_id not in user_data:
        return

    step = user_data[user_id].get("step")

    if step == "name":
        user_data[user_id]["name"] = message.text
        user_data[user_id]["step"] = "problem"
        await message.answer("Қандай техника бұзылды?")
    elif step == "problem":
        user_data[user_id]["problem"] = message.text
        user_data[user_id]["step"] = "location"
        kb = ReplyKeyboardMarkup(
            keyboard=[[KeyboardButton(text="📍 Локация жіберу", request_location=True)]],
            resize_keyboard=True, one_time_keyboard=True
        )
        await message.answer("Адресіңізді жіберіңіз:", reply_markup=kb)

@dp.message(F.location)
async def get_location(message: Message):
    user_id = message.from_user.id
    if user_id not in user_data or user_data[user_id].get("step") != "location":
        return

    location = message.location
    user_data[user_id]["address"] = f"{location.latitude}, {location.longitude}"
    user_data[user_id]["map_url"] = f"https://maps.google.com/?q={location.latitude},{location.longitude}"
    user_data[user_id]["step"] = "phone"

    kb = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="📞 Номерді жіберу", request_contact=True)]],
        resize_keyboard=True, one_time_keyboard=True
    )
    await message.answer("Телефон нөміріңізді жіберіңіз:", reply_markup=kb)

@dp.message(F.contact)
async def get_phone(message: Message):
    user_id = message.from_user.id
    if user_id not in user_data or user_data[user_id].get("step") != "phone":
        return

    user_data[user_id]["phone"] = message.contact.phone_number
    data = user_data[user_id]

    text = (
        "📥 Жаңа заказ:\n\n"
        f"👤 Аты: {data['name']}\n"
        f"🛠 Проблема: {data['problem']}\n"
        f"📍 Адрес: {data['address']}\n"
        f"📞 Номер: {data['phone']}\n"
        f"📍 Орналасқан жер: {data['map_url']}"
    )
    await bot.send_message(chat_id=ADMIN_ID, text=text)
    await message.answer("Рақмет! заказ қабылданды.")

    # Очищаем данные
    user_data.pop(user_id, None)

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
