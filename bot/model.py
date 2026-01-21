import os
import psycopg2
from Nodes import *


class Database:
    def __init__(self):
        """
        Подключение к БД
        Args:
            db_url = URL базы данных
        """
        db_url = os.getenv('DATABASE_URL')

        # подключение к postgresql
        self.connection = psycopg2.connect(db_url)
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

    def add_nodes(self, user_id, Nodes):
        """
        Добавление заметки в БД
        """
        try:
            self.cursor.execute(
            """INSERT INTO notes (user_id, title, content) 
            VALUES (%s, %s, %s) RETURNING id""", (user_id, Nodes.title, Nodes.content)
            )

            # получение обратного ID заметки из БД
            note_id = self.cursor.fetchone()[0]
            self.connection.commit()
            return note_id
        
        except:
            self.connection.rollback()
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
        except:
            return []