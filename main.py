import config
import telebot
from telebot import types
from database import Database

db = Database('db.db')
bot = telebot.TeleBot(config.TOKEN)

def main_menu():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton('👤 Поиск собеседника')
    markup.add(btn1)
    return markup

def stop_dialog():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton('✏️ Отправить свой профиль')
    btn2 = types.KeyboardButton('/❌Стоп')
    markup.add(btn1, btn2)
    return markup

def stop_search():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton('❌ Остановить поиск')
    markup.add(btn1)
    return markup

@bot.message_handler(commands = ['start'])
def start(message):
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        btn1 = types.KeyboardButton('Я парень 👨')
        btn2 = types.KeyboardButton('Я девушка 👩')
        markup.add(btn1, btn2)
        bot.send_message(message.chat.id, '{0.first_name}, добро пожаловать в анонимный чат!\nУкажите ваш пол!'.format(message.from_user), reply_markup = markup)



@bot.message_handler(commands = ['📜Меню'])
def menu(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton('👤 Поиск собеседника')
    markup.add(btn1)
    bot.send_message(message.chat.id, 'Меню'.format(message.from_user), reply_markup = markup)

@bot.message_handler(commands = ['❌Стоп'])
def stop(message):
    chat_info = db.get_active_chat(message.chat.id)
    if chat_info != False:
        db.delete_chat(chat_info[0])
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        btn1 = types.KeyboardButton('✏️ Следующий диалог')
        btn2 = types.KeyboardButton('/📜Меню')
        markup.add(btn1, btn2)
        bot.send_message(chat_info[1],'❌ Собеседник покинул чат', reply_markup = markup)
        bot.send_message(message.chat.id,'❌ Вы вышли из чата', reply_markup = markup)
    else:
        bot.send_message(message.chat.id,'❌ Вы не начали чат', reply_markup = markup)


@bot.message_handler(content_types=['text'])
def bot_message(message):
    if message.chat.type == 'private':
        if message.text == "👤 Поиск собеседника" or message.text == '✏️ Следующий диалог':
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            btn1 = types.KeyboardButton('🔎 Рандом')
            btn2 = types.KeyboardButton('🔎 Парень')
            btn3 = types.KeyboardButton('🔎 Девушка')
            markup.add(btn1, btn2, btn3)
            bot.send_message(message.chat.id, 'Кого искать?', reply_markup=markup)

        elif message.text == "❌ Остановить поиск":
            db.delete_queue(message.chat.id)
            bot.send_message(message.chat.id, '❌ Поиск остановлен.', reply_markup=main_menu())
        
        elif message.text == '✏️ Отправить свой профиль':
            chat_info = db.get_active_chat(message.chat.id)
            if chat_info != False:
                if message.from_user.username:
                    bot.send_message(chat_info[1], 'Профиль вашего собеседника @' + message.from_user.username)
                    bot.send_message(message.chat.id, '✏️ Вы отправили свой профиль собеседнику')
                else:
                    bot.send_message(message.chat.id, '❌ В вашем аккаунте не указан username!')
            else:
                bot.send_message(message.chat.id, '❌ Вы не начали диалог!')

        elif message.text == '🔎 Рандом':
            user_info = db.get_chat() # берём собеседника который стоит в очереди первым
            chat_two = user_info[0]

            if db.create_chat(message.chat.id, chat_two) == False:
                db.add_queue(message.chat.id, db.get_gender(message.chat.id))
                bot.send_message(message.chat.id, '👻 Поиск собеседника', reply_markup = stop_search())
            else:
                msg = 'Собеседник найден.\nЧто-бы остановить диалог, напишите: /❌Стоп'
                bot.send_message(message.chat.id, msg, reply_markup=stop_dialog())
                bot.send_message(chat_two, msg, reply_markup=stop_dialog())

        elif message.text == '🔎 Парень':
            user_info = db.get_gender_chat('male')
            chat_two = user_info[0]
            if db.create_chat(message.chat.id, chat_two) == False:
                db.add_queue(message.chat.id, db.get_gender(message.chat.id))
                bot.send_message(message.chat.id, '👻 Поиск собеседника', reply_markup = stop_search())
            else:
                msg = 'Собеседник найден.\nЧто-бы остановить диалог, напишите: /❌Стоп'
                bot.send_message(message.chat.id, msg, reply_markup=stop_dialog())
                bot.send_message(chat_two, msg, reply_markup=stop_dialog())

        elif message.text == '🔎 Девушка':
            user_info = db.get_gender_chat('female')
            chat_two = user_info[0]
            if db.create_chat(message.chat.id, chat_two) == False:
                db.add_queue(message.chat.id, db.get_gender(message.chat.id))
                bot.send_message(message.chat.id, '👻 Поиск собеседника', reply_markup = stop_search())
            else:
                msg = 'Собеседник найден.\nЧто-бы остановить диалог, напишите: /❌Стоп'
                bot.send_message(message.chat.id, msg, reply_markup=stop_dialog())
                bot.send_message(chat_two, msg, reply_markup=stop_dialog())


        elif message.text == 'Я парень 👨':
            if db.set_gender(message.chat.id, 'male'):
                bot.send_message(message.chat.id, '✅ Ваш пол успешно добавлен!', reply_markup=main_menu())
            else:
                bot.send_message(message.chat.id, '❌ Вы уже указали пол!', reply_markup=main_menu())

        elif message.text == 'Я девушка 👩':
            if db.set_gender(message.chat.id, 'female'):
                bot.send_message(message.chat.id, '✅ Ваш пол успешно добавлен!', reply_markup=main_menu())
            else:
                bot.send_message(message.chat.id, '❌ Вы уже указали пол!', reply_markup=main_menu)

        else:
            try:
                if db.get_active_chat(message.chat.id) != False:
                    chat_info = db.get_active_chat(message.chat.id)
                    bot.send_message(chat_info[1], message.text)
            except TypeError:
                    bot.send_message(message.chat.id, '❌ Вы не начали диалог!')

@bot.message_handler(content_types='sticker')
def bot_stickers(message):
    if message.chat.type == 'private':
        chat_info = db.get_active_chat(message.chat.id)
        file_id = message.sticker.file_id
        try:
            if chat_info != False:
                chat_info = db.get_active_chat(message.chat.id)
                bot.send_sticker(chat_info[1], file_id)
        except TypeError:
                bot.send_message(message.chat.id, '❌ Вы не начали диалог!')

@bot.message_handler(content_types='voice')
def bot_voice(message):
    if message.chat.type == 'private':
        chat_info = db.get_active_chat(message.chat.id)
        file_id = message.voice.file_id
        try:
            if chat_info != False:
                chat_info = db.get_active_chat(message.chat.id)
                bot.send_voice(chat_info[1], file_id)
        except TypeError:
                bot.send_message(message.chat.id, '❌ Вы не начали диалог!')

@bot.message_handler(content_types='photo')
def bot_photo(message):
    if message.chat.type == 'private':
        chat_info = db.get_active_chat(message.chat.id)
        file_id = message.photo[-1].file_id
        try:
            if chat_info != False:
                chat_info = db.get_active_chat(message.chat.id)
                bot.send_photo(chat_info[1], file_id)
        except TypeError:
                bot.send_message(message.chat.id, '❌ Вы не начали диалог!')

@bot.message_handler(content_types='audio')
def bot_audio(message):
    if message.chat.type == 'private':
        chat_info = db.get_active_chat(message.chat.id)
        file_id = message.audio.file_id
        try:
            if chat_info != False:
                chat_info = db.get_active_chat(message.chat.id)
                bot.send_audio(chat_info[1], file_id)
        except TypeError:
                bot.send_message(message.chat.id, '❌ Вы не начали диалог!')

@bot.message_handler(content_types='videonote')
def bot_videonote(message):
    if message.chat.type == 'private':
        chat_info = db.get_active_chat(message.chat.id)
        file_id = message.video_note.file_id
        try:
            if chat_info != False:
                chat_info = db.get_active_chat(message.chat.id)
                bot.send_video_note(chat_info[1], file_id)
        except TypeError:
                bot.send_message(message.chat.id, '❌ Вы не начали диалог!')

bot.polling(none_stop = True)