from flask import render_template, request, redirect, url_for, session, flash
from werkzeug.security import check_password_hash
from functools import wraps
import sqlite3
import math
from app.db import get_connection
from app import app
from config import Config

# Декоратор для защиты роутов, требующих авторизации
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'admin_logged_in' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        with get_connection(Config.DB_AUTH) as conn:
            user = conn.execute('SELECT * FROM admins WHERE username = ?', (username,)).fetchone()
            
        if user and check_password_hash(user['password_hash'], password):
            session['admin_logged_in'] = True
            session['username'] = username
            flash('Добро пожаловать!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Неверный логин или пароль')
            
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/')
@login_required
def index():
    page = request.args.get('page', 1, type=int)
    edit_id = request.args.get('edit', type=int)

    with get_connection(Config.DB_EXERCISES) as conn:
        total = conn.execute('SELECT COUNT(*) FROM exercises').fetchone()[0]
        total_pages = max(1, math.ceil(total / Config.ITEMS_PER_PAGE))
        page = max(1, min(page, total_pages))

        offset = (page - 1) * Config.ITEMS_PER_PAGE
        exercises = conn.execute(
            'SELECT * FROM exercises ORDER BY id LIMIT ? OFFSET ?',
            (Config.ITEMS_PER_PAGE, offset)
        ).fetchall()

    return render_template(
        'index.html',
        exercises=exercises,
        page=page,
        total_pages=total_pages,
        edit_id=edit_id
    )

@app.route('/add', methods=['POST'])
@login_required
def add():
    title = request.form['title']
    description = request.form['description']
    muscle_group = request.form['muscle_group']
    media_url = request.form['media_url']
    
    with get_connection(Config.DB_EXERCISES) as conn:
        conn.execute(
            'INSERT INTO exercises (title, description, muscle_group, media_url) VALUES (?, ?, ?, ?)',
            (title, description, muscle_group, media_url)
        )
        total = conn.execute('SELECT COUNT(*) FROM exercises').fetchone()[0]
    
    last_page = max(1, math.ceil(total / Config.ITEMS_PER_PAGE))
    return redirect(url_for('index', page=last_page))

@app.route('/edit/<int:item_id>', methods=['POST'])
@login_required
def edit(item_id):
    title = request.form['title']
    description = request.form['description']
    muscle_group = request.form['muscle_group']
    media_url = request.form['media_url']
    
    with get_connection(Config.DB_EXERCISES) as conn:
        conn.execute(
            'UPDATE exercises SET title = ?, description = ?, muscle_group = ?, media_url = ? WHERE id = ?',
            (title, description, muscle_group, media_url, item_id)
        )
        position = conn.execute(
            'SELECT COUNT(*) FROM exercises WHERE id < ?', (item_id,)
        ).fetchone()[0]
        
    page = max(1, (position // Config.ITEMS_PER_PAGE) + 1)
    return redirect(url_for('index', page=page))

@app.route('/delete/<int:item_id>')
@login_required
def delete(item_id):
    with get_connection(Config.DB_EXERCISES) as conn:
        conn.execute('DELETE FROM exercises WHERE id = ?', (item_id,))
        total = conn.execute('SELECT COUNT(*) FROM exercises').fetchone()[0]
        
    total_pages = max(1, math.ceil(total / Config.ITEMS_PER_PAGE))
    page = request.args.get('page', 1, type=int)
    page = min(page, total_pages)
    return redirect(url_for('index', page=page))

@app.route('/users')
@login_required
def users():
    try:
        with get_connection(Config.DB_BOT) as conn:
            # 1. Забираем всех пользователей из таблицы users
            all_users = conn.execute('SELECT * FROM users').fetchall()

            # 2. Забираем только АКТИВНЫЕ сессии
            active_sessions_rows = conn.execute('SELECT * FROM sessions WHERE is_active = 1').fetchall()

            # 3. Ключ мапы — user_id (Telegram ID)
            active_map = {str(s['user_id']): s for s in active_sessions_rows}

            # Для проверки в терминале при загрузке страницы:
            if all_users:
                print(f"DEBUG: ID первого юзера: {all_users[0]['user_id']}")
            print(f"DEBUG: Активные сессии для ID: {list(active_map.keys())}")

    except sqlite3.OperationalError as e:
        flash(f'Ошибка структуры БД: {e}', 'danger')
        all_users, active_map = [], {}

    return render_template('users.html', users=all_users, active_map=active_map)

@app.route('/terminate_session/<int:session_id>')
@login_required
def terminate_session(session_id):
    with get_connection(Config.DB_BOT) as conn:
        conn.execute('''
            UPDATE sessions 
            SET is_active = 0, ended_at = CURRENT_TIMESTAMP 
            WHERE id = ?
        ''', (session_id,))
        conn.commit()
    flash(f'Сессия #{session_id} принудительно завершена', 'success')
    return redirect(url_for('users'))