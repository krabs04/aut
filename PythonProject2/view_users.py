import sqlite3

def view_all_users():
    try:
        # Подключение к базе
        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()

        # Проверка таблицы
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users'")
        if not cursor.fetchone():
            print("❌ Таблица 'users' не найдена. Сначала создай базу через create_db.py.")
            return

        # Получение всех пользователей
        cursor.execute("SELECT * FROM users")
        users = cursor.fetchall()

        if users:
            print("📋 Зарегистрированные пользователи:")
            for user in users:
                user_id, username, password = user
                print(f"ID: {user_id}, Username: {username}, Password: {password}")
        else:
            print("📭 Пока нет зарегистрированных пользователей.")

        conn.close()

    except sqlite3.Error as e:
        print("Ошибка базы данных:", e)

if __name__ == "__main__":
    view_all_users()
