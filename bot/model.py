import os
import psycopg2
from Note import *


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