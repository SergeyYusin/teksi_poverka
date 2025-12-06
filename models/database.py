import sqlite3
import os
from config import Config


def get_db_connection():
    """Создает подключение к базе данных"""

    db_path = Config.DATABASE_PATH

    # Создаем папку data если её нет
    os.makedirs(os.path.dirname(db_path), exist_ok=True)

    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Инициализирует таблицы в базе данных"""

    conn = get_db_connection()
    cursor = conn.cursor()

    # Таблица заявок
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS applications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            full_name TEXT NOT NULL,
            address TEXT NOT NULL,
            phone TEXT NOT NULL,
            comment TEXT,
            selected_works TEXT,
            total_amount REAL DEFAULT 0,
            status TEXT DEFAULT 'new',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Таблица истории изменений
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS application_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            application_id INTEGER,
            action TEXT,
            details TEXT,
            changed_by TEXT DEFAULT 'system',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (application_id) REFERENCES applications (id)
        )
    ''')

    conn.commit()
    conn.close()