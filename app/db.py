import sqlite3
from werkzeug.security import generate_password_hash
from config import Config
import os

def init_db():
    """if os.path.exists(Config.DB_EXERCISES):
        return  # не пересоздаём, если уже есть"""

    with get_connection(Config.DB_EXERCISES) as conn:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS exercises (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                description TEXT,
                muscle_group TEXT,
                media_url TEXT
            )
        ''')
        """# Добавим базовые записи для теста
        sample_data = [
            ('Наклоны головы', 'Плавные наклоны головы вправо и влево.', 'Шея', 'https://example.com/neck.gif'),
            ('Вращение кистями', 'Разминка лучезапястного сустава.', 'Руки', 'https://example.com/hands.gif'),
            ('Потягушки', 'Вытянуть руки вверх, сцепив в замок.', 'Спина', 'https://example.com/back.gif'),
            ('Гимнастика для глаз', 'Рисуем глазами восьмерку.', 'Глаза', '')
        ]
        
        # Добиваем до 12 записей, чтобы сразу проверить пагинацию
        for i in range(5, 13):
            sample_data.append((f'Упражнение {i}', f'Описание для упражнения {i}', 'Общее', ''))

        for ex in sample_data:
            conn.execute(
                'INSERT INTO exercises (title, description, muscle_group, media_url) VALUES (?, ?, ?, ?)',
                ex
            )"""

    #Таблица АДМИНОВ
    with get_connection(Config.DB_AUTH) as conn:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS admins (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL UNIQUE,
                password_hash TEXT NOT NULL
            )
        ''')

        admin_user = os.environ.get("ADMIN_USERNAME")
        admin_pass = os.environ.get("ADMIN_PASSWORD")
        if not admin_user or not admin_pass:
            print("Ошибка: ADMIN_USERNAME или ADMIN_PASSWORD не заданы в переменных окружения.")
        else:
            #Проверяем, есть ли админ, если нет - создаём дефолтного
            admin_exists = conn.execute('SELECT * FROM admins LIMIT 1').fetchone()
            if not admin_exists:
                hashed_pass = generate_password_hash(admin_pass)
                try:
                    conn.execute(
                        'INSERT INTO admins (username, password_hash) VALUES (?, ?)',
                        (admin_user, hashed_pass)
                    )
                    conn.commit()
                    print(f"Администратор '{admin_user}' успешно создан.")
                except Exception as e:
                    print(f"Ошибка при создании админа: {e}")

def get_connection(db_name):
    conn = sqlite3.connect(db_name)
    conn.row_factory = sqlite3.Row
    return conn
