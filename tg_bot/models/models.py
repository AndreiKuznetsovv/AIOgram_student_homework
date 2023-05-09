from sqlalchemy import Column, Integer, String, UniqueConstraint, ForeignKey
from sqlalchemy.orm import relationship

from tg_bot.misc.database import Base


class Teacher(Base):
    # имя таблицы в postgres
    __tablename__ = "teachers"

    id = Column(Integer, primary_key=True)
    full_name = Column(String(100), nullable=False)
    tg_username = Column(String(100), nullable=False, unique=True)
    # relationship на таблицу Task (тк каждое задание должно быть закреплено за преподавателем)
    tasks = relationship('Task', passive_deletes=True, lazy=True)

class Task(Base):
    # имя таблицы в postgres
    __tablename__ = "tasks"
    # в таблице не может быть задания с совокупностью одинаковых группы предмета и названия
    __table_args__ = (UniqueConstraint('group', 'subject', 'task_name', name='task_unique_key'),)

    id = Column(Integer, primary_key=True)
    group = Column(String(7), nullable=False)
    subject = Column(String(100), nullable=False)
    task_name = Column(String(100), nullable=False)
    description = Column(String(255), nullable=True)
    # Внешний ключ на таблицу Teacher
    teacher_id = Column(ForeignKey('teachers.id', ondelete='CASCADE'), nullable=False)
    # relationship на таблицу File (тк каждый файл должен быть прикреплен к какому-то заданию)
    files = relationship('File', passive_deletes=True, lazy=True)


class File(Base):
    # имя таблицы в postgres
    __tablename__ = "files"

    id = Column(Integer, primary_key=True)
    code = Column(String(255), nullable=False)
    # Внешний ключ на таблицу Task
    task_id = Column(ForeignKey('tasks.id', ondelete='CASCADE'), nullable=False)
