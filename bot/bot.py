import os
import telebot
from telebot import types
from dotenv import load_dotenv
from Note import Note
from model import Database
from User import User

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")

bot = telebot.TeleBot(BOT_TOKEN)

db = Database()

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
        bot.delete_message(chat_id=message.chat.id,message_id=message.message_id)
        msg = bot.edit_message_text(chat_id=message.chat.id,message_id=oldMessage.message.message_id,text=f"Название заметки сохраненно: {title}.\n Введите текст заметки:",reply_markup=markup)
        bot.register_next_step_handler(msg,handleNoteText,userId,oldMessage)
    except Exception as e:
        print(e)
        bot.edit_message_text(chat_id=message.chat.id,message_id=oldMessage.message.message_id, text="Что-то пошло не так")

def handleNoteText(message,userId,oldMessage):
    try:
        markup = types.InlineKeyboardMarkup()
        btnBack = types.InlineKeyboardButton("Назад", callback_data = "mainMenu")
        btnAdd = types.InlineKeyboardButton("Добавить заметку", callback_data="addNote")
        markup.add(btnAdd,btnBack)
        text1 = message.text.strip()
        if not text1:
            msg = bot.edit_message_text(chat_id=message.chat.id,message_id=oldMessage.message.message_id, text="Текст заметки не может быть пустым",reply_markup=markup)
            bot.register_next_step_handler(msg,handleNoteText,userId,oldMessage)
            return
        
        userTempData[userId]['text'] = text1
        bot.delete_message(chat_id=message.chat.id,message_id=message.message_id)
        msg = bot.edit_message_text(chat_id=message.chat.id,message_id=oldMessage.message.message_id,text=f"Созданная заметка:\n{userTempData[userId]['title']}\n\n{text1}.",reply_markup=markup)
    except Exception as e:
        print(e)
        bot.edit_message_text(chat_id=message.chat.id,message_id=oldMessage.message.message_id,text="Что-то пошло не так",reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data == "addNote")
def addNote(call):
    try:
        bot.answer_callback_query(call.id)
        note = Note(
            userTempData[call.from_user.id]['title'],
            userTempData[call.from_user.id]['text']
            )
        userId = call.from_user.id
        username = call.from_user.username
        db_user_id = db.add_user(userId, username)
        db.add_note(db_user_id, note)
        confirmText = "Заметка успешно добавлена!"
        markup = types.InlineKeyboardMarkup()
        btnMenu = types.InlineKeyboardButton("Меню", callback_data="mainMenu")
        markup.add(btnMenu)
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=confirmText,reply_markup=markup)
    except Exception as e:
        print("USER")
        print(userId, username)
        print(type(userId),type(username))
        print(e)
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="Что-то пошло не так")
        
@bot.callback_query_handler(func=lambda call: call.data == "viewNotes")
def viewNotes(call):
    try:
        bot.answer_callback_query(call.id)
        
    except Exception as e:
        print(e)
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="Что-то пошло не так")


@bot.callback_query_handler(func=lambda call: call.data == "deleteNote")
def deleteNote(call):
    try:
        bot.answer_callback_query(call.id)
    except Exception as e:
        print(e)
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="Что-то пошло не так")

#Чтобы бот не переставал работать
bot.polling(none_stop=True)