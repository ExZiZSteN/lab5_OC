import os
import telebot
from telebot import types
from Note import Note
from model import Database
from User import User
from main import bot, db


#Ключ id пользователя, значение словарь с ключами 'title' и 'text'
userTempData = {}

user_states = {}

@bot.message_handler(commands=['start'])
def start(message):
    markup = types.InlineKeyboardMarkup()
    btnContinue = types.InlineKeyboardButton("Продолжить",callback_data = "mainMenu")
    markup.add(btnContinue)
    sendMessage = f'Привет, {message.from_user.first_name}! Я бот для создания и управления заметками'
    msg = bot.send_message(message.chat.id,sendMessage, reply_markup=markup)


@bot.callback_query_handler(func=lambda call: call.data == "mainMenu")
def menu(call):
    try:
        user_id = call.from_user.id
        if user_id in userTempData:
            del userTempData[user_id]
        if user_id in user_states:
            del user_states[user_id]
        bot.clear_step_handler_by_chat_id(call.message.chat.id)
        bot.answer_callback_query(call.id)
        markup = types.InlineKeyboardMarkup()
        btnCreate = types.InlineKeyboardButton("Создать заметку", callback_data = "createNote")
        btnView = types.InlineKeyboardButton("Просмотреть заметки", callback_data = "viewNotes")
        markup.add(btnCreate, btnView)
        newText = "Выберите действие:"
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text = newText, reply_markup = markup)
    except Exception as e:
       print(e)
       bot.send_message(call.message.chat.id, "Что-то пошло не так") 

@bot.callback_query_handler(func=lambda call: call.data == "createNote")
def createNote(call):
    try:
        bot.answer_callback_query(call.id)
        user_id = call.from_user.id
        user_states[user_id] = 'creating_note'
        newText = "Создать заметку\n Формат (Название заметки) (Текст заметки)\n Двумя разными сообщенимями."
        markup = types.InlineKeyboardMarkup()
        btnBack = types.InlineKeyboardButton("Назад", callback_data = "mainMenu")
        markup.add(btnBack)
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text = newText, reply_markup=markup)
        bot.register_next_step_handler(call.message,handleNoteName,user_id,call.message.message_id)  
    except Exception as e:
        print(e)
        bot.send_message(call.message.chat.id, "Что-то пошло не так")

def handleNoteName(message,userId,oldMessage):

    if userId not in user_states or user_states.get(userId) != 'creating_note':
        # Пользователь вышел из состояния создания заметки
        try:
            bot.delete_message(message.chat.id, message.message_id)
        except:
            pass
        return
    try:
        title = message.text.strip()
        markup = types.InlineKeyboardMarkup()
        btnBack = types.InlineKeyboardButton("Назад", callback_data = "mainMenu")
        markup.add(btnBack)
        if not title:
            msg = bot.edit_message_text(chat_id=message.chat.id,message_id=oldMessage, text="Название заметки не может быть пустым",reply_markup=markup)
            bot.register_next_step_handler(msg,handleNoteName,userId,oldMessage)
            return    
        if len(title) > 50:
            msg = bot.edit_message_text(chat_id=message.chat.id,message_id=oldMessage, text="Название слишком длинное. Введите короче",reply_markup=markup)
            bot.register_next_step_handler(msg,handleNoteName,userId,oldMessage)
            return
        
        userTempData[userId] = {'title':title}
        bot.delete_message(chat_id=message.chat.id,message_id=message.message_id)
        msg = bot.edit_message_text(chat_id=message.chat.id,message_id=oldMessage,text=f"Название заметки сохраненно: {title}.\n Введите текст заметки:",reply_markup=markup)
        bot.register_next_step_handler(msg,handleNoteText,userId,oldMessage)    
    except Exception as e:
        print(e)
        bot.edit_message_text(chat_id=message.chat.id,message_id=oldMessage, text="Что-то пошло не так")

def handleNoteText(message,userId,oldMessage):
    if userId not in user_states or user_states.get(userId) != 'creating_note':
        # Пользователь вышел из состояния создания заметки
        try:
            bot.delete_message(message.chat.id, message.message_id)
        except:
            pass
        return
    try:
        markup = types.InlineKeyboardMarkup()
        btnBack = types.InlineKeyboardButton("Назад", callback_data = "mainMenu")
        btnAdd = types.InlineKeyboardButton("Добавить заметку", callback_data="addNote")
        markup.add(btnAdd,btnBack)
        text1 = message.text.strip()
        if not text1:
            msg = bot.edit_message_text(chat_id=message.chat.id,message_id=oldMessage, text="Текст заметки не может быть пустым",reply_markup=markup)
            bot.register_next_step_handler(msg,handleNoteText,userId,oldMessage)
            return
        
        userTempData[userId]['text'] = text1
        bot.delete_message(chat_id=message.chat.id,message_id=message.message_id)
        msg = bot.edit_message_text(chat_id=message.chat.id,message_id=oldMessage,text=f"Созданная заметка:\n{userTempData[userId]['title']}\n\n{text1}.",reply_markup=markup)
    except Exception as e:
        print(e)
        bot.edit_message_text(chat_id=message.chat.id,message_id=oldMessage,text="Что-то пошло не так",reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data == "addNote")
def addNote(call):
    
    try:
        bot.answer_callback_query(call.id)
        note = Note()
        note.setTitle(userTempData[call.from_user.id]['title'])
        note.setContent(userTempData[call.from_user.id]['text'])
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
        print(e)
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="Что-то пошло не так")
        
@bot.callback_query_handler(func=lambda call: call.data == "viewNotes")
def viewNotes(call):
    try:
        userId = call.from_user.id
        user_states[userId] = 'view_notes'
        bot.answer_callback_query(call.id)
        db_user_id = db.get_userId(userId)
        if db_user_id is None:
            markup = types.InlineKeyboardMarkup()
            btnBack = types.InlineKeyboardButton("Назад", callback_data = "mainMenu")
            markup.add(btnBack)
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="У вас нет заметок. Сначала создайте заметку.",reply_markup=markup)
            return
        notes = db.get_user_notes(db_user_id)
        markup = types.InlineKeyboardMarkup()
        btnBack = types.InlineKeyboardButton("Назад", callback_data = "mainMenu")
        markup.add(btnBack)
        if not notes:
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="У вас нет заметок. Сначала создайте заметку.",reply_markup=markup)
            return
        notesText = "Ваши заметки:\n(Для редактирования напшити id заметки)\n\n"
        for note in notes:
            notesText += f"id: {note.id}\nНазвание: {note.title} \n\n"
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=notesText,reply_markup=markup)
        bot.register_next_step_handler(call.message,editNote,userId,call)
    except Exception as e:
        print(e)
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="Что-то пошло не так")

def editNote(message,userId,oldMessage):
    if userId not in user_states or user_states.get(userId) != 'view_notes':
        # Пользователь вышел из состояния просмотра заметки
        try:
            bot.delete_message(message.chat.id, message.message_id)
        except:
            pass
        return
    try:
        noteId = message.text.strip()
        if not noteId.isdigit():
            markup = types.InlineKeyboardMarkup()
            btnBack = types.InlineKeyboardButton("Назад", callback_data = "mainMenu")
            markup.add(btnBack)
            msg = bot.edit_message_text(chat_id=message.chat.id,message_id=oldMessage.message.message_id, text="Введите корректный id заметки",reply_markup=markup)
            bot.register_next_step_handler(msg,editNote,userId,oldMessage)
            return
        bot.delete_message(chat_id=message.chat.id,message_id=message.message_id)
        noteId = int(noteId)
        note = db.get_note_by_id(noteId)
        if note is None:
            markup = types.InlineKeyboardMarkup()
            btnBack = types.InlineKeyboardButton("Назад", callback_data = "mainMenu")
            markup.add(btnBack)
            msg = bot.edit_message_text(chat_id=message.chat.id,message_id=oldMessage.message.message_id, text="Заметка с таким id не найдена. Введите корректный id заметки",reply_markup=markup)
            bot.register_next_step_handler(msg,editNote,userId,oldMessage)
            return
        markup = types.InlineKeyboardMarkup()
        btnDelete = types.InlineKeyboardButton("Удалить заметку", callback_data=f"deleteNote_{note.id}")
        btnBack = types.InlineKeyboardButton("Назад", callback_data = "mainMenu")
        markup.add(btnDelete,btnBack)
        bot.edit_message_text(chat_id=message.chat.id, message_id=oldMessage.message.message_id, text=f"Заметка с id={noteId}\n Название: {note.getTitle()}\n Текст: {note.getContent()}\n\n выбрана для редактирования, вы можете ввести новый текст заметки", reply_markup=markup)
        bot.register_next_step_handler(oldMessage.message,handleEditNoteText,note,oldMessage)
    except Exception as e:
        print(e)
        bot.edit_message_text(chat_id=message.chat.id,message_id=oldMessage.message.message_id, text="Что-то пошло не так")

def handleEditNoteText(message,note,oldMessage):
    userId = message.from_user.id
    if userId not in user_states or user_states.get(userId) != 'view_notes':
        # Пользователь вышел из состояния просмотра заметки
        try:
            bot.delete_message(message.chat.id, message.message_id)
        except:
            pass
        return
    try:
        newText = message.text.strip()
        if not newText:
            markup = types.InlineKeyboardMarkup()
            btnBack = types.InlineKeyboardButton("Назад", callback_data = "mainMenu")
            markup.add(btnBack)
            msg = bot.edit_message_text(chat_id=message.chat.id,message_id=oldMessage.message.message_id, text="Текст заметки не может быть пустым",reply_markup=markup)
            bot.register_next_step_handler(msg,handleEditNoteText,note,oldMessage)
            return
        bot.delete_message(chat_id=message.chat.id,message_id=message.message_id)
        note.setContent(newText)
        db.update_note(note)
        confirmText = f"Заметка успешно отредактирована!\n\nid: {note.id}\nНазвание: {note.getTitle()}\nНовое содержимое: \n " + newText
        markup = types.InlineKeyboardMarkup()
        btnDelete = types.InlineKeyboardButton("Удалить заметку", callback_data=f"deleteNote_{note.id}")
        btnMenu = types.InlineKeyboardButton("Меню", callback_data="mainMenu")
        markup.add(btnDelete, btnMenu)
        bot.edit_message_text(chat_id=message.chat.id,message_id=oldMessage.message.message_id,text=confirmText,reply_markup=markup)
    except Exception as e:
        print(e)
        bot.edit_message_text(chat_id=message.chat.id,message_id=oldMessage.message.message_id,text="Что-то пошло не так")


@bot.callback_query_handler(func=lambda call: call.data.startswith("deleteNote_"))
def deleteNote(call):
    try:
        markup = types.InlineKeyboardMarkup()
        btnBack = types.InlineKeyboardButton("Назад", callback_data = "mainMenu")
        markup.add(btnBack)
        bot.answer_callback_query(call.id)
        noteId = call.data.split("_")[1]
        db.delete_note(noteId)
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="Заметка удалена",reply_markup=markup)
    except Exception as e:
        print(e)
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="Что-то пошло не так")

#Чтобы бот не переставал работать
bot.polling(none_stop=True)