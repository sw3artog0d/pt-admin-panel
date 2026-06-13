from config import settings
from sqlalchemy import select
from werkzeug.security import generate_password_hash
from app.models import Base, Admin
from app.db import engine, session_factory

def init_db():
    Base.metadata.create_all(engine)

    with session_factory() as db_session:
        admin_user = settings.ADMIN_USERNAME
        admin_pass = settings.ADMIN_PASSWORD

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