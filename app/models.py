from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey, text, Integer, String
from typing import Optional, Annotated
import enum, datetime

intpk = Annotated[int, mapped_column(primary_key=True)]
timestamp = Annotated[datetime.datetime, mapped_column(server_default=text("(CURRENT_TIMESTAMP)"))]

class Base(DeclarativeBase):
    pass

class Exercise(Base):
    __tablename__ = "exercises"
    id: Mapped[intpk]
    title: Mapped[str] = mapped_column(String(100))
    description: Mapped[str | None] = mapped_column(String(255))
    muscle_group: Mapped[str] = mapped_column(String(50))
    media_url: Mapped[str | None] = mapped_column(String(255))

class Admin(Base): 
    __tablename__ = "admins"
    id: Mapped[intpk]
    username: Mapped[str] = mapped_column(String(30), unique=True)
    password_hash: Mapped[str]

class User(Base):
    __tablename__ = "users"
    id: Mapped[intpk]
    user_id: Mapped[int]
    username: Mapped[str | None] = mapped_column(String(50))
    first_name: Mapped[str | None] = mapped_column(String(50))

    sessions: Mapped[list["UserSession"]] = relationship(back_populates="user")

class UserSession(Base):
    __tablename__ = "sessions"
    id: Mapped[intpk]
    user_id: Mapped[int] = mapped_column(ForeignKey("users.user_id"))
    started_at: Mapped[timestamp]
    ended_at: Mapped[datetime.datetime | None]
    is_active: Mapped[bool]
    
    user: Mapped["User"] = relationship(back_populates="sessions")