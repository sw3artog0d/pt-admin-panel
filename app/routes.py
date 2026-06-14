from flask import render_template, request, redirect, url_for, session, flash
from werkzeug.security import check_password_hash
from functools import wraps
from app import app
from app.dao import (
    get_admin_by_username,
    get_exercises_paginated,
    add_exercise,
    update_exercise,
    delete_exercise,
    get_users_with_active_sessions,
    deactivate_session,
)

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
        user = get_admin_by_username(username)

        if user and check_password_hash(user.password_hash, password):
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

    exercises, page, total_pages = get_exercises_paginated(page)

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
    last_page = add_exercise(title, description, muscle_group, media_url)
    
    return redirect(url_for('index', page=last_page))


@app.route('/edit/<int:item_id>', methods=['POST'])
@login_required
def edit(item_id):
    title = request.form['title']
    description = request.form['description']
    muscle_group = request.form['muscle_group']
    media_url = request.form['media_url']
    page = update_exercise(item_id, title, description, muscle_group, media_url)

    return redirect(url_for('index', page=page))


@app.route('/delete/<int:item_id>')
@login_required
def delete(item_id):
    requested_page = request.args.get('page', 1, type=int)
    page = delete_exercise(item_id, requested_page)

    return redirect(url_for('index', page=page))


@app.route('/users')
@login_required
def users():
     # Инициализируем пустыми значениями на случай ошибки
    all_users = [] 
    active_map = {}
    try:
        all_users, active_map = get_users_with_active_sessions()
    except Exception as e:
        flash(f'Ошибка структуры БД: {e}', 'danger')
        all_users, active_map = [], {}

    return render_template('users.html', users=all_users, active_map=active_map)


@app.route('/terminate_session/<int:session_id>')
@login_required
def terminate_session(session_id):
    deactivate_session(session_id)
    flash(f'Сессия #{session_id} принудительно завершена', 'success')
    return redirect(url_for('users'))