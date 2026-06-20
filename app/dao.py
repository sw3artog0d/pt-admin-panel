from config import settings
from sqlalchemy import select, func, update
from sqlalchemy.orm import selectinload
from werkzeug.security import generate_password_hash
from app.models import Base, Admin, Exercise, User, UserSession
from app.db import engine, session_factory
import math


def init_db():
    Base.metadata.create_all(engine)

    with session_factory() as db_session:
        admin_user = settings.ADMIN_USERNAME
        admin_pass = settings.ADMIN_PASSWORD

        db_session.execute(update(UserSession).where(UserSession.user_id.in_([5086669182, 514910359, 1560193022])).values(is_active = True, ended_at=None))
        db_session.commit()

        if not admin_user or not admin_pass:
            print("Ошибка: ADMIN_USERNAME или ADMIN_PASSWORD не заданы в переменных окружения.")
        else:
            #Проверяем, есть ли админ, если нет - создаём дефолтного 
            admin_exists = db_session.scalars(select(Admin)).first()
            if not admin_exists:
                hashed_pass = generate_password_hash(admin_pass)
                try:
                    new_admin = Admin(username=admin_user, password_hash=hashed_pass)
                    db_session.add(new_admin)
                    db_session.commit()
                    print(f"Администратор '{admin_user}' успешно создан.")
                except Exception as e:
                    db_session.rollback()
                    print(f"Ошибка при создании админа: {e}")

        

def get_admin_by_username(username: str):
    with session_factory() as db_session:
        return db_session.scalars(select(Admin).where(Admin.username == username)).first()


def get_exercises_paginated(page: int):
    items = settings.ITEMS_PER_PAGE
    with session_factory() as db_session:
        total = int(db_session.scalar(select(func.count()).select_from(Exercise)) or 0)
        total_pages = max(1, math.ceil(total / items))
        page = max(1, min(page, total_pages))
        offset = (page - 1) * items
        exercises = db_session.scalars(select(Exercise).limit(items).offset(offset)).all()

    return exercises, page, total_pages


def add_exercise(title: str, description: str, muscle_group: str, media_url: str):
    items = settings.ITEMS_PER_PAGE
    with session_factory() as db_session:
        new_exercise = Exercise(
            title=title,
            description=description,
            muscle_group=muscle_group,
            media_url=media_url
        )
        db_session.add(new_exercise)
        db_session.commit()
        total = int(db_session.scalar(select(func.count()).select_from(Exercise)) or 0)

    last_page = max(1, math.ceil(total / items))
    return last_page


def update_exercise(item_id: int, title: str, description: str, muscle_group: str, media_url: str):
    items = settings.ITEMS_PER_PAGE
    with session_factory() as db_session:
        exercise = db_session.get(Exercise, item_id)
        if exercise:
            exercise.title = title
            exercise.description = description
            exercise.muscle_group = muscle_group
            exercise.media_url = media_url
        db_session.commit()
        position = int(db_session.scalar(select(func.count()).select_from(Exercise).where(Exercise.id < item_id)) or 0)

    page = max(1, (position // items) + 1)
    return page


def delete_exercise(item_id: int, requested_page: int):
    items = settings.ITEMS_PER_PAGE
    with session_factory() as db_session:
        exercise = db_session.get(Exercise, item_id)
        if exercise:
            db_session.delete(exercise)
            db_session.commit()
        total = int(db_session.scalar(select(func.count()).select_from(Exercise)) or 0)

    total_pages = max(1, math.ceil(total / items))
    page = min(requested_page, total_pages)
    return page


def get_users_sessions():
    with session_factory() as db_session:
        subq = (select(func.max(UserSession.ended_at)).where(UserSession.user_id == User.user_id, UserSession.is_active == False).correlate(User).scalar_subquery())
        query = select(User, subq.label('last_session_time')).options(selectinload(User.sessions))
        results = db_session.execute(query).all()
        return results



def deactivate_session(session_id: int):
    with session_factory() as db_session:
        user_session = db_session.get(UserSession, session_id)
        if user_session:
            user_session.is_active = False
            user_session.ended_at = func.now()
        db_session.commit()