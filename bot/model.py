import os
import psycopg2
from Note import *
from User import User
from dotenv import load_dotenv


load_dotenv()

class Database:
    def __init__(self):
        """
        Подключение к БД
        Args:
            db_url = URL базы данных
        """
        db_url = os.getenv('DATABASE_URL')

        # подключение к postgresql
        # self.connection = psycopg2.connect(db_url)
        # self.cursor = self.connection.cursor()
        self.connection = psycopg2.connect(
            dbname=os.getenv("POSTGRES_DB"),
            user=os.getenv("POSTGRES_USER"),
            password=os.getenv("POSTGRES_PASSWORD"),
            host="localhost",
            port=5432
        )
        self.cursor = self.connection.cursor()
        self.create_tables()

    def create_tables(self):
        """
        Создание таблиц в БД
        """
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS users(
                id SERIAL PRIMARY KEY,
                telegram_id BIGINT UNIQUE NOT NULL,
                username VARCHAR(255)
            )
                            """)
        
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS notes(
                id SERIAL PRIMARY KEY,
                user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                title VARCHAR(255) NOT NULL,
                content TEXT NOT NULL
            )
                            """)
        
        self.connection.commit()

    def add_user(self, telegramId, username):
        """
        Добавление пользователя
        
        Args:
            telegramId: ID в телеграме
            username: Имя пользователя в телеграме
        """
        try:
            self.cursor.execute("""
                INSERT INTO users (telegram_id, username)
                VALUES (%s, %s)
                ON CONFLICT (telegram_id) DO NOTHING
                RETURNING id
            """, (telegramId, username))

            row = self.cursor.fetchone()
            self.connection.commit()

            if row:                  # новый пользователь
                return row[0]

            # если пользователь уже был
            self.cursor.execute("SELECT id FROM users WHERE telegram_id = %s", (telegramId,))
            return self.cursor.fetchone()[0]
        except Exception as e:
            print(e)
            self.connection.rollback()
            return None

    def add_note(self, user_id, Note):
        """
        Добавление заметки в БД

        Args:
            user_id: id пользователя
            Note: заметка
        """
        try:
            self.cursor.execute(
            """INSERT INTO notes (user_id, title, content) 
            VALUES (%s, %s, %s) RETURNING id""", (user_id, Note.title, Note.content)
            )

            # получение обратного ID заметки из БД
            note_id = self.cursor.fetchone()[0]
            self.connection.commit()
            return note_id
        
        except Exception as e:
            print(e)
            self.connection.rollback()
            return None

    def get_userId(self,telegramID):
        """
        Получение ID пользователя по его telegram ID
        """
        try:
            self.cursor.execute("""
                SELECT id 
                FROM users 
                WHERE telegram_id = %s
            """, (telegramID,))

            row = self.cursor.fetchone()
            if not row:
                return None
            
            return row[0]
        except Exception as e:
            print(e)
            return None

    def get_user_notes(self, user_id):
        """
        Получение всех заметок пользователя
        """
        try:
            self.cursor.execute("""
                SELECT id, title, content 
                FROM notes 
                WHERE user_id = %s 
                                 """, (user_id))

            columns = ['id', 'title', 'content']
            notes = []
        
            # создание словарей с отображением в них параметров заметки из БД
            for row in self.cursor.fetchall():
                note_dict = {}
                for i, column in enumerate(columns):
                    note_dict[column] = row[i]
                notes.append(note_dict)
            return notes   
        except Exception as e:
            print(e)
            return []
        
    def get_note_by_id(self, note_id):
        """
        Получить заметку по ID
        """
        try:
            self.cursor.execute("""
                SELECT id, title, content
                FROM notes 
                WHERE id = %s
            """, (note_id))

            # проверка строки на наличие данных
            row = self.cursor.fetchone()
            if not row:
                return None
            
            # создание словаря с параметрами из БД
            columns = ['id', 'title', 'content']
            return dict(zip(columns, row))
    
        except Exception as e:
            print(e)
            return None
        
    def update_note(self, note_id, content=None):
        """
        Обновить заметку
        Args:
            updates = хранение обновлённых частей
            params = хранение обновлённых значений
        """
        try:
            self.cursor.execute(f"""
                UPDATE notes
                SET {content} 
                WHERE id = %s
                RETURNING id
                """, (note_id))

            updated = self.cursor.fetchone() is not None

            if updated:
                self.connection.commit()

            return updated  
        except Exception as e:
            print(e)
            return False

    def delete_note(self, note_id):
        """
        Удалить заметку
        """
        try:
            self.cursor.execute("""
                DELETE FROM notes 
                WHERE id = %s
                RETURNING id
            """, (note_id))

            # проверка удаления записи
            deleted = self.cursor.fetchone() is not None
            if deleted:
                self.connection.commit()
            
            return deleted
    
        except Exception as e:
            print(e)
            return False