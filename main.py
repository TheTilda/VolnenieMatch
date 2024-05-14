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
    edit = State()
    edit_name = State()
    edit_age = State()
    edit_city = State()
    edit_description = State()
    edit_college = State()
    edit_anket = State()
    get_reaction = State()
    get_answer_reaction = State()

main_kb = ReplyKeyboardMarkup(resize_keyboard=True)
main_kb.add(KeyboardButton('Смотреть анкеты✌️'), KeyboardButton('Моя анкета👤'))
main_kb.add('Мои ответы на заявки🤩')

async def render_edit_kb(user_id):
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add(KeyboardButton('Сохранить'), KeyboardButton('Редактировать'))
    return kb
    
@dp.message_handler(commands=['start'])
async def start_handler(message,  state: FSMContext):
    req = await db.add_user(message.from_user.id, message.from_user.username)
    if req == 'succes create user':
        await bot.send_message(message.chat.id, '<b>Привет! Я бот для знакомств на конкурсе ВОЛНЕНИЕ</b>.\nКак тебя зовут?:')
        await Form.name.set()
    else:
        await bot.send_message(message.chat.id, 'Вы в главном меню', reply_markup=main_kb)

@dp.message_handler(state=Form.name)
async def get_name(message, state: FSMContext):
    await db.change_name(message.from_user.id, message.text)
    await message.reply("<b>Приятно познакомиться!😁</b>\nИз какого ты учебного учреждения?\n<i>*Если ты организатор/куратор команды, напиши из какого ты предприятия</i>")#Приятно познакомиться!😁</b>\n
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
        await message.reply('Осталось еще чуть-чуть...🙃 Из какого ты города?', reply_markup=types.ReplyKeyboardRemove())
        await Form.city.set()
    elif message.text == 'Женский👩🏻‍🦰':
        await db.change_gender(message.from_user.id, 1)
        await message.reply('Осталось еще чуть-чуть...🙃 Из какого ты города?', reply_markup=types.ReplyKeyboardRemove())
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
    await db.change_bio(message.from_user.id, message.text)

    msg = await message.reply('Теперь отправь свои фото или видео которые будут видеть другие пользователи (максимум 3)\n|Загружено файлов: 0', reply_markup=InlineKeyboardMarkup(resize_keyboard=True).add(InlineKeyboardButton('Завершить загрузку', callback_data='cancel_upload')))
    async with state.proxy() as data:
        data['msg'] = msg.message_id
    await Form.images.set()

@dp.message_handler(state=Form.images, content_types=['photo', 'video'])
async def get_images(message, state: FSMContext):
    file_id = ''
    if message.content_type == 'photo':
        file_id = message.photo[-1].file_id
    elif message.content_type == 'video':
        file_id = message.video.file_id
    elif message.content_type == 'video_note':
        file_id = message.video_note.file_id
    
    
    count = await db.check_count_files(message.from_user.id)
    ##print(count)
    await message.delete()
    async with state.proxy() as data:
        if (await db.check_count_files(message.from_user.id)) < 3:
            await db.upload_file(message.from_user.id, file_id, message.content_type)
            try:
                await bot.edit_message_text(chat_id=message.chat.id, message_id=int(data['msg']), text=f"Теперь отправь свои фото или видео которые будут видеть другие пользователи (максимум 3)\n|Загружено файлов: {await db.check_count_files(message.from_user.id)}",  reply_markup=InlineKeyboardMarkup(resize_keyboard=True).add(InlineKeyboardButton('Завершить загрузку', callback_data='cancel_upload')))
            except:
                pass
        else:
            await bot.delete_message(message.from_user.id, data['msg'])
            anket = await db.get_anket(message.from_user.id)
            media = types.MediaGroup()

            await bot.send_message(message.chat.id, 'Супер! Твоя анкета готова, сейчас она выглядит так:', reply_markup=(await render_edit_kb(message.from_user.id)))
            for i in anket['images']:
                if i['file_type'] == 'video':
                    if count == 0:
                        media.attach_video(i['file_id'], caption=f"{anket['user']['name']}, {anket['user']['age']}, {anket['user']['city']}, {anket['user']['college']}.\n{anket['user']['description']}")
                    else:
                        media.attach_video(i['file_id'])
                    
                else:
                    if count == 0:
                        media.attach_photo(i['file_id'], caption=f"{anket['user']['name']}, {anket['user']['age']}, {anket['user']['city']}, {anket['user']['college']}.\n{anket['user']['description']}")
                    else:
                        media.attach_photo(i['file_id'])
                count+=1
            await bot.send_media_group(message.from_user.id, media=media)
            await Form.edit.set()
    
@dp.callback_query_handler(state=Form.images, text='cancel_upload')
async def cancel_upload(callback_query, state: FSMContext):
    if await db.check_count_files(callback_query.from_user.id) < 1:
        await bot.send_message(callback_query.from_user.id, 'Для продолжения отправьте минимум 1 медиа')
    else:
        async with state.proxy() as data:
            await bot.delete_message(callback_query.from_user.id, data['msg'])
            anket = await db.get_anket(callback_query.from_user.id)
            #print(anket)
            media = types.MediaGroup()
            count = 0
            await bot.send_message(callback_query.from_user.id, 'Супер! Твоя анкета готова, сейчас она выглядит так:', reply_markup=(await render_edit_kb(callback_query.from_user.id)))
            for i in anket['images']:
                if i['file_type'] == 'video':
                    if count == 0:
                        media.attach_video(i['file_id'], caption=f"{anket['user']['name']}, {anket['user']['age']}, {anket['user']['city']}, {anket['user']['college']}.\n{anket['user']['description']}")
                    else:
                        media.attach_video(i['file_id'])
                    
                else:
                    if count == 0:
                        media.attach_photo(i['file_id'], caption=f"{anket['user']['name']}, {anket['user']['age']}, {anket['user']['city']}, {anket['user']['college']}.\n{anket['user']['description']}")
                    else:
                        media.attach_photo(i['file_id'])
                count+=1
            await bot.send_media_group(callback_query.from_user.id, media=media)
            await Form.edit.set()

@dp.message_handler(state=Form.edit)
async def edit_anket(message, state: FSMContext):
    if message.text == 'Сохранить':
        await bot.send_sticker(message.chat.id, "CAACAgIAAxkBAAEZrghmOJszAAFk_yGXz7V5BiVSoPUmXKsAAkUDAAK1cdoGk4gQHIncDRs1BA")
        await message.reply('Анкета сохранена! Вы в главном меню', reply_markup=main_kb)
        await db.save_anket(message.from_user.id)
        await state.finish()
    elif message.text == 'Редактировать':
        kb = InlineKeyboardMarkup()
        kb.add(InlineKeyboardButton('Изменить имя', callback_data=f'ch_name_{message.from_user.id}'))
        kb.add(InlineKeyboardButton('Изменить возраст', callback_data=f'ch_age_{message.from_user.id}'))
        kb.add(InlineKeyboardButton('Изменить город', callback_data=f'ch_city_{message.from_user.id}'))
        kb.add(InlineKeyboardButton('Изменить ссуз', callback_data=f'ch_college_{message.from_user.id}'))
        kb.add(InlineKeyboardButton('Изменить описание', callback_data=f'ch_description_{message.from_user.id}'))
        kb.add(InlineKeyboardButton('Изменить фотографии', callback_data=f'ch_image_{message.from_user.id}'))
        await message.reply('Редактирование анкеты', reply_markup=kb)
        await state.finish()
    else:
        await message.reply('Выбери вариант из списка')

@dp.callback_query_handler(text_startswith = 'ch_')
async def change(callback_query, state: FSMContext):
    type_edit = callback_query.data.split('_')[1]
    if type_edit == 'name':
        await bot.edit_message_text(chat_id=callback_query.from_user.id, message_id=callback_query.message.message_id, text='Напишите новое имя', reply_markup=InlineKeyboardMarkup().add(InlineKeyboardButton('Отмена', callback_data='back')))
        await Form.edit_name.set()
    elif type_edit == 'age':
        await bot.edit_message_text(chat_id=callback_query.from_user.id, message_id=callback_query.message.message_id, text='Напишите новый возраст', reply_markup=InlineKeyboardMarkup().add(InlineKeyboardButton('Отмена', callback_data='back')))
        await Form.edit_age.set()

    elif type_edit == 'city':
        await bot.edit_message_text(chat_id=callback_query.from_user.id, message_id=callback_query.message.message_id, text='Напишите новое город', reply_markup=InlineKeyboardMarkup().add(InlineKeyboardButton('Отмена', callback_data='back')))
        await Form.edit_city.set()

    elif type_edit == 'college':
        await bot.edit_message_text(chat_id=callback_query.from_user.id, message_id=callback_query.message.message_id, text='Напишите новое место обучения', reply_markup=InlineKeyboardMarkup().add(InlineKeyboardButton('Отмена', callback_data='back')))
        await Form.edit_college.set()

    elif type_edit == 'description':
        await bot.edit_message_text(chat_id=callback_query.from_user.id, message_id=callback_query.message.message_id, text='Напишите новое описание', reply_markup=InlineKeyboardMarkup().add(InlineKeyboardButton('Отмена', callback_data='back')))
        await Form.edit_description.set()

    elif type_edit == 'image':
        msg = await bot.edit_message_text(chat_id=callback_query.from_user.id, message_id=callback_query.message.message_id, text='Теперь отправь свои фото или видео которые будут видеть другие пользователи (максимум 3)\n|Загружено файлов: 0', reply_markup=InlineKeyboardMarkup(resize_keyboard=True).add(InlineKeyboardButton('Завершить загрузку', callback_data='cancel_upload')))
        await db.delete_images(callback_query.from_user.id)
        async with state.proxy() as data:
            data['msg'] = msg.message_id
        await Form.images.set()

@dp.message_handler(state=Form.edit_name)
async def edit_name(message, state: FSMContext):
    await db.change_name(message.from_user.id, message.text)
    await bot.send_message(message.chat.id, 'Успешно отредактировано! Вы в главном меню', reply_markup=main_kb)
    await db.save_anket(message.from_user.id)
    await state.finish()
@dp.message_handler(state=Form.edit_age)
async def edit_age(message, state: FSMContext):
    if message.text.isdigit():
        await db.change_age(message.from_user.id, message.text)
        await bot.send_message(message.chat.id, 'Успешно отредактировано! Вы в главном меню', reply_markup=main_kb)
        await db.save_anket(message.from_user.id)

        await state.finish()
    else:
        await message.reply('Отправьте возраст числом')
@dp.message_handler(state=Form.edit_city)
async def edit_city(message, state: FSMContext):
    await db.change_city(message.from_user.id, message.text)
    await bot.send_message(message.chat.id, 'Успешно отредактировано! Вы в главном меню', reply_markup=main_kb)
    await db.save_anket(message.from_user.id)
    await state.finish()

@dp.message_handler(state=Form.edit_college)
async def edit_college(message, state: FSMContext):
    await db.change_college(message.from_user.id, message.text)
    await bot.send_message(message.chat.id, 'Успешно отредактировано! Вы в главном меню', reply_markup=main_kb)
    await db.save_anket(message.from_user.id)
    await state.finish()

@dp.message_handler(state=Form.edit_description)
async def edit_bio(message, state: FSMContext):
    await db.change_bio(message.from_user.id, message.text)
    await bot.send_message(message.chat.id, 'Успешно отредактировано! Вы в главном меню', reply_markup=main_kb)
    await db.save_anket(message.from_user.id)
    await state.finish()

@dp.message_handler(text="Моя анкета👤")
async def my_anket(message):
    anket = await db.get_anket(message.from_user.id)
    media = types.MediaGroup()
    count = 0
    await bot.send_message(message.from_user.id, 'Cейчас твоя анкета выглядит так', reply_markup=ReplyKeyboardMarkup(resize_keyboard=True).add(KeyboardButton('Редактировать анкету✏️'), KeyboardButton('Удалить анкету⭕️')).add(InlineKeyboardButton('В главное меню⬅️')))
    for i in anket['images']:
        if i['file_type'] == 'video':
            if count == 0:
                media.attach_video(i['file_id'], caption=f"{anket['user']['name']}, {anket['user']['age']}, {anket['user']['city']}, {anket['user']['college']}.\n{anket['user']['description']}")
            else:
                media.attach_video(i['file_id'])
            
        else:
            if count == 0:
                media.attach_photo(i['file_id'], caption=f"{anket['user']['name']}, {anket['user']['age']}, {anket['user']['city']}, {anket['user']['college']}.\n{anket['user']['description']}")
            else:
                media.attach_photo(i['file_id'])
        count+=1
    await bot.send_media_group(message.from_user.id, media=media)
    await Form.edit_anket.set()

@dp.message_handler(text="Смотреть анкеты✌️")
async def view_ankets(message, state: FSMContext):
    
    await bot.send_sticker(message.chat.id, "CAACAgIAAxkBAAEZtDpmOv-IchOMSw775H63dyOAHnM0yAACTwMAArVx2gZq1OIofocaZDUE", reply_markup=ReplyKeyboardMarkup(resize_keyboard=True).add(KeyboardButton("👎"), KeyboardButton("👍")).add(KeyboardButton('Не хочу больше никого искать🧐')))
    anket = await db.get_random_anket(message.from_user.id)
    async with state.proxy() as data:
        data['direct_id'] = anket
    if (anket) is None:
        await message.reply('На сегодня для тебя нет анкет', reply_markup=main_kb)
        await state.finish()
    else:
        user = await db.get_anket(anket)
        media = types.MediaGroup()
        count = 0
        for i in user['images']:
            if i['file_type'] == 'video':
                if count == 0:
                    media.attach_video(i['file_id'], caption=f"{user['user']['name']}, {user['user']['age']}, {user['user']['city']}, {user['user']['college']}.\n{user['user']['description']}")
                else:
                    media.attach_video(i['file_id'])
                
            else:
                if count == 0:
                    media.attach_photo(i['file_id'], caption=f"{user['user']['name']}, {user['user']['age']}, {user['user']['city']}, {user['user']['college']}.\n{user['user']['description']}")
                else:
                    media.attach_photo(i['file_id'])
            count+=1
        await bot.send_media_group(message.from_user.id, media=media)
        await Form.get_reaction.set()

@dp.message_handler(state=Form.get_reaction)
async def get_reaction(message, state: FSMContext):
    reaction = 0 #1 отрицаительная реакция, 2 положительная, 0 игнор
    async with state.proxy() as data:
        if message.text == '👎' or message.text == "👍":
            if message.text == '👎':
                reaction = 1
            elif message.text == '👍':
                reaction = 2
                await bot.send_message(data['direct_id'], 'Твоя анкета кому-то понравилась, посмотреть можно в главном меню🚀')
            await db.set_reaction(message.from_user.id, data['direct_id'], reaction=reaction)
            anket = await db.get_random_anket(message.from_user.id)
            async with state.proxy() as data:
                data['direct_id'] = anket
            if (anket) is None:
                await message.reply('На сегодня для тебя нет анкет', reply_markup=main_kb)
                await state.finish()
            else:
                user = await db.get_anket(anket)
                media = types.MediaGroup()
                count = 0
                for i in user['images']:
                    if i['file_type'] == 'video':
                        if count == 0:
                            media.attach_video(i['file_id'], caption=f"{user['user']['name']}, {user['user']['age']}, {user['user']['city']}, {user['user']['college']}.\n{user['user']['description']}")
                        else:
                            media.attach_video(i['file_id'])
                        
                    else:
                        if count == 0:
                            media.attach_photo(i['file_id'], caption=f"{user['user']['name']}, {user['user']['age']}, {user['user']['city']}, {user['user']['college']}.\n{user['user']['description']}")
                        else:
                            media.attach_photo(i['file_id'])
                    count+=1
                await bot.send_media_group(message.from_user.id, media=media)

        elif message.text == "Не хочу больше никого искать🧐":
            await bot.send_sticker(message.from_user.id, "CAACAgIAAxkBAAEZrdFmOJAlTWmd4-R-XeeP9_gNeDdlCQACUwMAArVx2gbtH-L5lSdj5DUE", reply_markup=main_kb)
            await bot.send_message(message.from_user.id,'Вы в главном меню')
            await state.finish()
        else:
            await message.reply('Я тебя не понимаю, выбери вариант из списка👇')

        
    


@dp.message_handler(state=Form.edit_anket)
async def my_anket_edit(message, state: FSMContext):
    if message.text == 'Удалить анкету⭕️':
        #Отправка грустного стикера
        await bot.send_sticker(message.from_user.id, "CAACAgIAAxkBAAEZrbpmOIfQHXuQ7e99tYeOliBJlbCnBwACVwMAArVx2ga2e7f7gIXrkjUE", reply_markup=types.ReplyKeyboardRemove())
        await bot.send_message(message.from_user.id, 'Вы уверены?', reply_markup=InlineKeyboardMarkup().add(InlineKeyboardButton('Да, удалить❌', callback_data="del_ok"), InlineKeyboardButton('Нет, оставить✅', callback_data="del_no")))
        await state.finish()
    elif message.text == 'Редактировать анкету✏️':
        await bot.send_sticker(message.from_user.id, "CAACAgIAAxkBAAEZrcBmOIlHscVZwK0fwz4fYJvj779_FQACRAMAArVx2gYMtzsTtIZDMDUE", reply_markup=types.ReplyKeyboardRemove())
        kb = InlineKeyboardMarkup()
        kb.add(InlineKeyboardButton('Изменить имя', callback_data=f'ch_name_{message.from_user.id}'))
        kb.add(InlineKeyboardButton('Изменить возраст', callback_data=f'ch_age_{message.from_user.id}'))
        kb.add(InlineKeyboardButton('Изменить город', callback_data=f'ch_city_{message.from_user.id}'))
        kb.add(InlineKeyboardButton('Изменить ссуз', callback_data=f'ch_college_{message.from_user.id}'))
        kb.add(InlineKeyboardButton('Изменить описание', callback_data=f'ch_description_{message.from_user.id}'))
        kb.add(InlineKeyboardButton('Изменить фотографии', callback_data=f'ch_image_{message.from_user.id}'))
        kb.add(InlineKeyboardButton('Назад◀️', callback_data='back'))
        await message.reply('Редактирование анкеты', reply_markup=kb)
        await state.finish()
    elif message.text == 'В главное меню⬅️':
        await bot.send_sticker(message.from_user.id, "CAACAgIAAxkBAAEZrdFmOJAlTWmd4-R-XeeP9_gNeDdlCQACUwMAArVx2gbtH-L5lSdj5DUE", reply_markup=main_kb)
        await bot.send_message(message.from_user.id,'Вы в главном меню')
        await state.finish()

@dp.callback_query_handler(text="back")
async def back(callback_query):
    await bot.send_sticker(callback_query.from_user.id, "CAACAgIAAxkBAAEZrdFmOJAlTWmd4-R-XeeP9_gNeDdlCQACUwMAArVx2gbtH-L5lSdj5DUE", reply_markup=main_kb)
    await bot.send_message(callback_query.from_user.id,'Вы в главном меню')

@dp.callback_query_handler(text_startswith = 'del_')
async def delete_account(callback_query):
    #print(callback_query.data)
    if callback_query.data.split('_')[1] == 'ok':
        await callback_query.message.delete()
        await db.delete_anket(callback_query.from_user.id)
        await bot.send_message(callback_query.from_user.id, 'Ваша анкета удалена, она больше не будет показываться другим пользователям. Если вы хотите снова создать анкету, используйте команду /start')
    else:
        await bot.delete_message(callback_query.from_user.id, (callback_query.message.message_id-1)) 
        await bot.delete_message(callback_query.from_user.id, callback_query.message.message_id )
        await bot.send_message(callback_query.from_user.id, 'Вы в гланом меню', reply_markup=main_kb)

@dp.message_handler(state=Form.get_answer_reaction)
async def get_answ_reaction(message, state: FSMContext):
    reaction = 0
    if message.text == "👎":
        reaction = 1
    elif message.text == '👍':
        reaction = 2
        async with state.proxy() as data:
            await bot.send_message(message.chat.id, f'Отлично! Cвязаться с этим пользоватлем можно по ссылке: t.me/{await db.get_username(data["first_id"])}', reply_markup=main_kb)
            await bot.send_message(int(data['first_id']), f'Отлично! Твоя анкета обрела взаимность, связаться с пользователем можно по ссылке: t.me/{message.from_user.username}', reply_markup=main_kb)
    async with state.proxy() as data:
        await db.set_direct_reaction(data['first_id'], message.from_user.id, reaction=reaction)
    ankets = await db.get_anket_where_not_ckeck(message.from_user.id)
    io =''
    try:
        io = ankets[0]['first_id']
    except:
        await bot.send_message(message.from_user.id, 'Вы в гланом меню', reply_markup=main_kb)
        await state.finish()
        
    anket = await db.get_random_anket(io)
    if anket:
        await bot.send_sticker(message.chat.id, "CAACAgIAAxkBAAEZtDpmOv-IchOMSw775H63dyOAHnM0yAACTwMAArVx2gZq1OIofocaZDUE", reply_markup=ReplyKeyboardMarkup(resize_keyboard=True).add(KeyboardButton("👎"), KeyboardButton("👍")))
        user = await db.get_anket(anket)
        media = types.MediaGroup()
        count = 0
        
        for i in user['images']:
            if i['file_type'] == 'video':
                if count == 0:
                    media.attach_video(i['file_id'], caption=f"{user['user']['name']}, {user['user']['age']}, {user['user']['city']}, {user['user']['college']}.\n{user['user']['description']}")
                else:
                    media.attach_video(i['file_id'])
                
            else:
                if count == 0:
                    media.attach_photo(i['file_id'], caption=f"{user['user']['name']}, {user['user']['age']}, {user['user']['city']}, {user['user']['college']}.\n{user['user']['description']}")
                else:
                    media.attach_photo(i['file_id'])
            count+=1
        async with state.proxy() as data:
            data['first_id'] = anket[0]['first_id']
        
        await bot.send_media_group(message.from_user.id, media=media)
    else:
        await state.finish()
    

@dp.message_handler(state="*")
async def other_hanlder(message, state: FSMContext):
    if message.text == 'Мои ответы на заявки🤩':
        ankets = await db.get_anket_where_not_ckeck(message.from_user.id)
        print(ankets)
        anket = await db.get_anket(ankets[0]['first_id'])
        if (anket) is None:
            await message.reply('На сегодня для тебя нет анкет', reply_markup=main_kb)
        else:
            await bot.send_sticker(message.chat.id, "CAACAgIAAxkBAAEZtDpmOv-IchOMSw775H63dyOAHnM0yAACTwMAArVx2gZq1OIofocaZDUE", reply_markup=ReplyKeyboardMarkup(resize_keyboard=True).add(KeyboardButton("👎"), KeyboardButton("👍")))
            user = await db.get_anket(anket['user']['user_id'])
            media = types.MediaGroup()
            count = 0
            
            for i in user['images']:
                if i['file_type'] == 'video':
                    if count == 0:
                        media.attach_video(i['file_id'], caption=f"{user['user']['name']}, {user['user']['age']}, {user['user']['city']}, {user['user']['college']}.\n{user['user']['description']}")
                    else:
                        media.attach_video(i['file_id'])
                    
                else:
                    if count == 0:
                        media.attach_photo(i['file_id'], caption=f"{user['user']['name']}, {user['user']['age']}, {user['user']['city']}, {user['user']['college']}.\n{user['user']['description']}")
                    else:
                        media.attach_photo(i['file_id'])
                count+=1
            async with state.proxy() as data:
                data['first_id'] = ankets[0]['first_id']
            
            await bot.send_media_group(message.from_user.id, media=media)
            await Form.get_answer_reaction.set()
            





if __name__ == '__main__':
    executor.start_polling(dp)