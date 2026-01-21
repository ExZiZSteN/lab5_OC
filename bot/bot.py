import os
import telebot
from telebot import types
from dotenv import load_dotenv
from Note import Note

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")

bot = telebot.TeleBot(BOT_TOKEN)


#Ключ id пользователя, значение словарь с ключами 'title' и 'text'
userTempData = {}


@bot.message_handler(commands=['start'])
def start(message):
    markup = types.InlineKeyboardMarkup()
    btnContinue = types.InlineKeyboardButton("Продолжить",callback_data = "mainMenu")
    markup.add(btnContinue)
    sendMessage = f'Привет, {message.from_user.first_name}! Я бот для создания и управления заметками'
    msg = bot.send_message(message.chat.id,sendMessage, reply_markup=markup)


@bot.callback_query_handler(func=lambda call: call.data == "mainMenu")
def continue1(call):
    try:
        bot.answer_callback_query(call.id)
        markup = types.InlineKeyboardMarkup()
        btnCreate = types.InlineKeyboardButton("Создать заметку", callback_data = "createNote")
        btnView = types.InlineKeyboardButton("Просмотреть заметки", callback_data = "viewNotes")
        btnDelete = types.InlineKeyboardButton("Удалить заметку", callback_data="deleteNote")
        markup.add(btnCreate, btnView, btnDelete)
        newText = "Выберите действие:"
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text = newText, reply_markup = markup)
    except Exception as e:
       print(e)
       bot.send_message(call.message.chat.id, "Что-то пошло не так") 

@bot.callback_query_handler(func=lambda call: call.data == "createNote")
def createNote(call):
    try:
        bot.answer_callback_query(call.id)
        newText = "Создать заметку\n Формат (Название заметки) (Текст заметки)\n Двумя разными сообщенимями."
        markup = types.InlineKeyboardMarkup()
        btnBack = types.InlineKeyboardButton("Назад", callback_data = "mainMenu")
        markup.add(btnBack)
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text = newText, reply_markup=markup)
        bot.register_next_step_handler(call.message,handleNoteName,call.from_user.id,call)
    except Exception as e:
        print(e)
        bot.send_message(call.message.chat.id, "Что-то пошло не так")

def handleNoteName(message,userId,oldMessage):
    try:
        title = message.text.strip()
        markup = types.InlineKeyboardMarkup()
        btnBack = types.InlineKeyboardButton("Назад", callback_data = "mainMenu")
        markup.add(btnBack)
        if not title:
            msg = bot.edit_message_text(chat_id=message.chat.id,message_id=oldMessage.message.message_id, text="Название заметки не может быть пустым",reply_markup=markup)
            bot.register_next_step_handler(msg,handleNoteName,userId,oldMessage)
            return
        if len(title) > 50:
            msg = bot.edit_message_text(chat_id=message.chat.id,message_id=oldMessage.message.message_id, text="Название слишком длинное. Введите короче",reply_markup=markup)
            bot.register_next_step_handler(msg,handleNoteName,userId,oldMessage)
            return
        
        userTempData[userId] = {'title':title}

        msg = bot.edit_message_text(chat_id=message.chat.id,message_id=oldMessage.message.message_id,text=f"Название заметки сохраненно: {title}.\n Введите текст заметки:",reply_markup=markup)
        bot.register_next_step_handler(msg,handleNoteText,userId,oldMessage)
    except Exception as e:
        print(e)
        bot.edit_message_text(chat_id=message.chat.id,message_id=oldMessage.message.message_id, text="Что-то пошло не так")

def handleNoteText(message,userId,oldMessage):
    try:
        markup = types.InlineKeyboardMarkup()
        btnBack = types.InlineKeyboardButton("Назад", callback_data = "mainMenu")
        markup.add(btnBack)
        text1 = message.text.strip()
        if not text1:
            msg = bot.edit_message_text(chat_id=message.chat.id,message_id=oldMessage.message.message_id, text="Текст заметки не может быть пустым",reply_markup=markup)
            bot.register_next_step_handler(msg,handleNoteText,userId,oldMessage)
            return
        
        userTempData[userId]['text'] = text1
    except Exception as e:
        print(e)
        bot.edit_message_text(chat_id=message.chat.id,message_id=oldMessage.message.message_id,text="Что-то пошло не так",reply_markup=markup)


#Чтобы бот не переставал работать
bot.polling(none_stop=True)