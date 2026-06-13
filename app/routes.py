from flask import render_template, request, redirect, url_for, session, flash
from werkzeug.security import check_password_hash
from functools import wraps
from sqlalchemy import func, select
from sqlalchemy.exc import SQLAlchemyError
import math
from app.db import session_factory
from app import app
from config import settings
from app.models import Admin, Exercise, User, UserSession

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
        
        with session_factory() as db_session:
            user = db_session.scalars(select(Admin).where(Admin.username == username)).first()
            
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

    with session_factory() as db_session:
        total = db_session.scalar(select(func.count()).select_from(Exercise))
        total_pages = max(1, math.ceil(total / settings.ITEMS_PER_PAGE))
        page = max(1, min(page, total_pages))

        offset = (page - 1) * settings.ITEMS_PER_PAGE
        exercises = db_session.scalars(select(Exercise).limit(settings.ITEMS_PER_PAGE).offset(offset)).all()

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
    
    with session_factory() as db_session:
        new_exercise = Exercise(
            title=title,
            description=description,
            muscle_group=muscle_group,
            media_url=media_url
        )
        db_session.add(new_exercise)
        db_session.commit()
        total = db_session.scalar(select(func.count()).select_from(Exercise))
    
    last_page = max(1, math.ceil(total / settings.ITEMS_PER_PAGE))
    return redirect(url_for('index', page=last_page))

@app.route('/edit/<int:item_id>', methods=['POST'])
@login_required
def edit(item_id):
    title = request.form['title']
    description = request.form['description']
    muscle_group = request.form['muscle_group']
    media_url = request.form['media_url']
    
    with session_factory() as db_session:
        exercise = db_session.get(Exercise, item_id)

        if exercise:
            exercise.title=title
            exercise.description=description
            exercise.muscle_group=muscle_group
            exercise.media_url=media_url

        db_session.commit()
        position = db_session.scalar(select(func.count()).select_from(Exercise).where(Exercise.id < item_id))
        
    page = max(1, (position // settings.ITEMS_PER_PAGE) + 1)
    return redirect(url_for('index', page=page))

@app.route('/delete/<int:item_id>')
@login_required
def delete(item_id):
    with session_factory() as db_session:
        exercise = db_session.get(Exercise, item_id)
        if exercise:
            db_session.delete(exercise)
            db_session.commit()
        total = db_session.scalar(select(func.count()).select_from(Exercise))
        
    total_pages = max(1, math.ceil(total / settings.ITEMS_PER_PAGE))
    page = request.args.get('page', 1, type=int)
    page = min(page, total_pages)
    return redirect(url_for('index', page=page))

@app.route('/users')
@login_required
def users():
     # Инициализируем пустыми значениями на случай ошибки
    all_users = [] 
    active_map = {}

    try:
        with session_factory() as db_session:
            # 1. Забираем всех пользователей из таблицы users
            all_users = db_session.scalars(select(User)).all()

            # 2. Забираем только АКТИВНЫЕ сессии
            active_sessions_rows = db_session.scalars(select(UserSession).where(UserSession.is_active == True)).all()

            # 3. Ключ мапы — user_id (Telegram ID)
            active_map = {str(s.user_id): s for s in active_sessions_rows}

            # Для проверки в терминале при загрузке страницы:
            if all_users:
                print(f"DEBUG: ID первого юзера: {all_users[0].user_id}")
            print(f"DEBUG: Активные сессии для ID: {list(active_map.keys())}")

    except SQLAlchemyError as e:
        flash(f'Ошибка структуры БД: {e}', 'danger')
        all_users, active_map = [], {}

    return render_template('users.html', users=all_users, active_map=active_map)

@app.route('/terminate_session/<int:session_id>')
@login_required
def terminate_session(session_id):
    with session_factory() as db_session:
        user_session = db_session.get(UserSession, session_id)
        if user_session:
            user_session.is_active = False
            user_session.ended_at = func.now()
        db_session.commit()
    flash(f'Сессия #{session_id} принудительно завершена', 'success')
    return redirect(url_for('users'))