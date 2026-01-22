import os
import telebot
from dotenv import load_dotenv
from model import Database

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")

if not BOT_TOKEN:
    raise ValueError("Токен не найден")

bot = telebot.TeleBot(BOT_TOKEN)
db = Database()

from bot import *
    
def main():
    try:
        bot.polling()

    except KeyboardInterrupt:
        print("Остановка бота")

    except Exception as e:
        print(e)
    finally:
        db.connection.close()
        
if __name__ == '__main__':
    main()