import os
import json
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart
from aiogram.types import KeyboardButton, ReplyKeyboardMarkup
from api import User
from dotenv import load_dotenv
from datetime import datetime, timezone, timedelta

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot=bot)

user_service = User()
user_cache = {}
moderator = "@oksanaminkevich"


@dp.message(CommandStart())
async def start_handler(message: types.Message):
    telegram_id = message.from_user.id
    web_app_url = f"https://stlthwl.github.io/bingosoft-meetup?telegram_id={telegram_id}"

    # Создание кнопки для ReplyKeyboardMarkup
    button = KeyboardButton(text="Перейти к регистрации", web_app={"url": web_app_url})
    markup = ReplyKeyboardMarkup(keyboard=[[button]], resize_keyboard=True)

    msg = "Вы получили приглашение на Pro.Meetup by BingoSoft.\nНажмите кнопку ниже, чтобы перейти на страницу регистрации."

    await message.answer(msg, reply_markup=markup)


# Обработчик для сообщений из веб-приложения
@dp.message(lambda message: message.web_app_data)
async def web_app_message_handler(message: types.Message):
    try:
        data = json.loads(message.web_app_data.data)

        moscow_time = message.date.replace(tzinfo=timezone.utc)
        moscow_time += timedelta(hours=3)  # Добавляем 3 часа для Москвы
        user_telegram_id = message.from_user.id
        user_cache[user_telegram_id] = {
            'formatted_date_time': moscow_time.strftime("%d.%m.%Y %H:%M"),
            'tg_first_name': message.from_user.first_name,
            'tg_last_name': message.from_user.last_name,
            'tg_user_name': message.from_user.username,
            'form_data': data
        }

        formatted_str = f"Имя в телеграм: {user_cache[user_telegram_id]['tg_first_name']}\n"
        formatted_str += f"Фамилия в телеграм: {user_cache[user_telegram_id]['tg_last_name']}\n"
        formatted_str += f"Никнейм в телеграм: " + f"@{user_cache[user_telegram_id]['tg_user_name']}\n" if \
            user_cache[user_telegram_id]['tg_user_name'] else "не указанn\n"
        formatted_str += f"telegram_id: {user_telegram_id}\n\n"
        formatted_str += f"Данные из формы: \n\n" + f"Имя: {user_cache[user_telegram_id]['form_data']['name']}\n"
        formatted_str += f"Фамилия: {user_cache[user_telegram_id]['form_data']['surname']}\n"
        formatted_str += f"Организация: {user_cache[user_telegram_id]['form_data']['organization']}\n"

        formatted_str += f"Должность: {user_cache[user_telegram_id]['form_data']['position']}\n"
        formatted_str += f"День 1, очное участие: {"Да" if user_cache[user_telegram_id]['form_data']['first_day_in_person'] else "Нет"}\n"
        formatted_str += f"Просмотр офиса: {"Да" if user_cache[user_telegram_id]['form_data']['first_day_office_observe'] else "Нет"}\n"
        formatted_str += f"День 2, гонка: {"Да" if user_cache[user_telegram_id]['form_data']['second_day_race'] else "Нет"}\n"
        formatted_str += f"Пилот болида 🚗: {"Да" if user_cache[user_telegram_id]['form_data']['pilot'] else "Нет"}\n"
        formatted_str += f"Болельщик 👀: {"Да" if user_cache[user_telegram_id]['form_data']['fan'] else "Нет"}\n"
        formatted_str += f"День 2, пикинк: {"Да" if user_cache[user_telegram_id]['form_data']['second_day_picnic'] else "Нет"}\n"
        formatted_str += f"Мастер класс: {"Да" if user_cache[user_telegram_id]['form_data']['master_class'] else "Нет"}\n"
        formatted_str += f"Баня: {"Да" if user_cache[user_telegram_id]['form_data']['sauna'] else "Нет"}\n"

        check_response = await user_service.get_user_by_telegram_id(message.chat.id)

        if check_response["code"] == 500:
            await bot.send_message(user_telegram_id, check_response['message'])
        elif check_response["code"] == 200:
            # print(check_response)
            await bot.send_message(message.chat.id, check_response["message"])
            await bot.send_message(chat_id=int(os.getenv('GROUP_ID')), text=f"Попытка повторной регистрации!\n\n" + formatted_str)
            await bot.send_message(user_telegram_id, f"Контакт модератора \n{moderator}")
            return
        else:
            response = await user_service.register_user(data)
            if response['code'] == 200:

                await bot.send_message(chat_id=int(os.getenv('GROUP_ID')), text="Зарегистрирован участник!\n\n" + formatted_str)
                await bot.send_message(user_telegram_id, f"Регистрация прошла успешно, ожидайте модерацию. Контакт модератора \n{moderator}")
            else:
                await bot.send_message(message.chat.id, response["message"])

    except Exception as e:
        print(e)
        await bot.send_message(message.from_user.id, "Сервис временно недоступен, попробуйте позже")


@dp.message()
async def message_handler(message: types.Message):
    # await message.reply(message.text) ### PLUG ###
    await start_handler(message)


async def main():
    try:
        await bot.delete_webhook()
        await dp.start_polling(bot)
    finally:
        await bot.session.close()


def start_bot():
    asyncio.create_task(main())


if __name__ == "__main__":
    asyncio.run(main())
