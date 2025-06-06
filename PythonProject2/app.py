from flask import Flask, request, redirect, url_for
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
import sqlite3
import os

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'

# --- Инициализация Flask-Login ---
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'  # Страница входа для неавторизованных

# --- Инициализация БД,
def init_db():
    if not os.path.exists('users.db'):
        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()
        cursor.execute('''
        CREATE TABLE users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL
        )
        ''')
        conn.commit()
        conn.close()

# --- Класс пользователя для Flask-Login ---
class User(UserMixin):
    def __init__(self, id, username, password):
        self.id = id
        self.username = username
        self.password = password

    @staticmethod
    def get(user_id):
        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE id = ?', (user_id,))
        user = cursor.fetchone()
        conn.close()
        if user:
            return User(id=user[0], username=user[1], password=user[2])
        return None

@login_manager.user_loader
def load_user(user_id):
    return User.get(user_id)

# --- Главная страница ---
@app.route('/')
def index():
    return '''
        <h2>Добро пожаловать!</h2>
        <a href="/login">Войти</a> | <a href="/register">Зарегистрироваться</a>
    '''

# --- Регистрация ---
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()
        try:
            cursor.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username, password))
            conn.commit()
            conn.close()
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            return '<h3>Имя пользователя уже занято. Попробуйте другое.</h3><a href="/register">Назад</a>'
    return '''
        <h2>Регистрация</h2>
        <form method="post">
            Имя: <input type="text" name="username"><br>
            Пароль: <input type="password" name="password"><br>
            <input type="submit" value="Зарегистрироваться">
        </form>
        <a href="/">Назад</a>
    '''

# --- Логин с Flask-Login ---
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE username = ? AND password = ?', (username, password))
        user_data = cursor.fetchone()
        conn.close()

        if user_data:
            user = User(id=user_data[0], username=user_data[1], password=user_data[2])
            login_user(user)  # Вход пользователя
            return redirect(url_for('home'))
        else:
            return '<h3>Неверные данные. Попробуйте снова.</h3><a href="/login">Назад</a>'
    return '''
        <h2>Вход</h2>
        <form method="post">
            Имя: <input type="text" name="username"><br>
            Пароль: <input type="password" name="password"><br>
            <input type="submit" value="Войти">
        </form>
        <a href="/">Назад</a>
    '''

# --- Защищённая домашняя страница ---
@app.route('/home')
@login_required
def home():
    return f'''
        <h2>Привет, {current_user.username}!</h2>
        <p>Вы успешно вошли.</p>
        <a href="/logout">Выйти</a>
    '''

# --- Выход ---
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

# --- Запуск ---
if __name__ == '__main__':
    init_db()
    app.run(debug=True)
