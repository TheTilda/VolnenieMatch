import aiogram.utils.markdown as md
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import ParseMode, WebAppInfo
from aiogram.utils import executor
from aiogram.types import ReplyKeyboardRemove, \
    ReplyKeyboardMarkup, KeyboardButton, \
    InlineKeyboardMarkup, InlineKeyboardButton, \
    CallbackQuery, message
from aiogram.utils.executor import start_webhook
from aiogram.contrib.middlewares.logging import LoggingMiddleware
import config
import database as db
from aiogram_broadcaster import MessageBroadcaster
from typing import List, Union
from aiogram.dispatcher.handler import CancelHandler
from aiogram.dispatcher.middlewares import BaseMiddleware
from datetime import datetime, date
from aiogram.types import ChatActions
import asyncio
import requests
import os
from urllib.parse import urlencode

bot = Bot(token=config.token, parse_mode='HTML')
dp = Dispatcher(bot, storage=MemoryStorage())

class Form(StatesGroup):
    name = State()
    college = State()
    age = State()
    gender = State()
    city = State()
    bio = State()
    images = State()

    
@dp.message_handler(commands=['start'])
async def start_handler(message,  state: FSMContext):
    req = await db.add_user(message.from_user.id)
    if req == 'succes create user':
        await bot.send_message(message.chat.id, '<b>Привет! Я бот для знакомств на конкурсе ВОЛНЕНИЕ</b>.\nКак тебя зовут?:')
        await Form.name.set()

@dp.message_handler(state=Form.name)
async def get_name(message, state: FSMContext):
    await db.change_name(message.from_user.id, message.text)
    await message.reply("<b>Приятно познакомиться!😁</b>\nИз какого ты учебного учреждения?")#Приятно познакомиться!😁</b>\n
    await Form.college.set()

@dp.message_handler(state=Form.college)
async def get_college(message, state: FSMContext):
    await db.change_college(message.from_user.id, message.text)
    await message.reply('<b>Сколько тебе лет?</b>')
    await Form.age.set()

@dp.message_handler(state=Form.age)
async def get_age(message, state: FSMContext):
    if message.text.isdigit():
        await db.change_age(message.chat.id, message.text)
        await message.reply('Выбери свой пол', reply_markup=ReplyKeyboardMarkup(resize_keyboard=True).add(KeyboardButton('Мужской👨🏻'), KeyboardButton('Женский👩🏻‍🦰')))
        await Form.gender.set()
    else:
        await message.reply('Напиши возраст <b>числом</b>')

@dp.message_handler(state=Form.gender)
async def get_gender(message, state: FSMContext):
    if message.text == "Мужской👨🏻":
        await db.change_gender(message.from_user.id, 1)
        await message.reply('Осталось еще чуть-чуть...🙃 Из какого ты города?')
        await Form.city.set()
    elif message.text == 'Женский👩🏻‍🦰':
        await db.change_gender(message.from_user.id, 1)
        await message.reply('Осталось еще чуть-чуть...🙃 Из какого ты города?')
        await Form.city.set()
    else:
        await message.reply('Выбери вариант из списка')

@dp.message_handler(state=Form.city)
async def get_city(message, state: FSMContext):
    await db.change_city(message.from_user.id, message.text)
    await message.reply('Предпоследний пункт: <b>кратко расскажи о себе😎</b>')
    await Form.bio.set()

@dp.message_handler(state=Form.bio)
async def get_bio(message, state: FSMContext):
    await db.change_city(message.from_user.id, message.text)

    msg = await message.reply('Теперь отправь свои фото, видео или кружки которые будут видеть другие пользователи (максимум 3)\n|Загружено файлов: 0', reply_markup=ReplyKeyboardMarkup(resize_keyboard=True).add(KeyboardButton('Завершить загрузку')))
    async with state.proxy() as data:
        data['msg'] = msg.message_id
    await Form.images.set()

@dp.message_handler(state=Form.images, content_types=['photo', 'video', 'video_note', 'text'])
async def get_images(message, state: FSMContext):
    if message.text == 'Завершить загрузку':
        await state.finish()
    file_id = ''
    if message.content_type == 'photo':
        file_id = message.photo[-1].file_id
    elif message.content_type == 'video':
        file_id = message.video.file_id
    elif message.content_type == 'video_note':
        file_id = message.video_note.file_id
    
    await db.upload_file(message.from_user.id, file_id, message.content_type)
    count = await db.check_count_files(message.from_user.id)
    print(count)
    if count <= 3:
        async with state.proxy() as data:
            await message.reply(f'Теперь отправь свои фото, видео или кружки которые будут видеть другие пользователи (максимум 3)\n|Загружено файлов: {count}', reply_markup=ReplyKeyboardMarkup(resize_keyboard=True).add(KeyboardButton('Завершить загрузку')))
    else:
        await message.reply('Супер! Твоя анкета готова, сейчас она выглядит так:')
        await state.finish()
    
    await message.delete()
    





if __name__ == '__main__':
    executor.start_polling(dp)