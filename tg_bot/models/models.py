from sqlalchemy import Column, Integer, String, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship

from tg_bot.misc.database import Base


# User table
class User(Base):
    # имя таблицы в postgres
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    full_name = Column(String(100), nullable=False)
    tg_username = Column(String(100), nullable=False, unique=True)
    # relationship на таблицу Teacher
    teacher = relationship('Teacher', back_populates='user', passive_deletes=True)
    # relationship на таблицу Student
    student = relationship('Student', back_populates='user', passive_deletes=True)


class Teacher(Base):
    # имя таблицы в postgres
    __tablename__ = "teachers"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False, unique=True)
    # relationship на таблицу User
    user = relationship('User', back_populates='teacher', passive_deletes=True)
    # relationship на таблицу TeacherSubject
    teachers_subjects = relationship('TeacherSubject', back_populates='teacher', passive_deletes=True)
    # relationship на таблицу Task
    tasks = relationship('Task', back_populates='teacher', passive_deletes=True)


class Student(Base):
    # имя таблицы в postgres
    __tablename__ = "students"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False, unique=True)
    group_id = Column(Integer, ForeignKey('groups.id', ondelete='CASCADE'), nullable=False)
    # relationship на таблицу User
    user = relationship('User', back_populates='student', passive_deletes=True)
    # relationship на таблицу Group
    group = relationship('Group', back_populates='student', passive_deletes=True)
    # relationship на таблицу Answer (ответы на задание)
    answers = relationship('Answer', back_populates='student', passive_deletes=True)

class Subject(Base):
    # имя таблицы в postgres
    __tablename__ = "subjects"

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False, unique=True)
    # relationship на таблицу TeacherSubjectGroupSubject
    teachers_subjects = relationship('TeacherSubject', back_populates='subject', passive_deletes=True)
    # relationship на таблицу GroupSubject
    groups_subjects = relationship('GroupSubject', back_populates='subject', passive_deletes=True)
    # relationship на таблицу Task
    tasks = relationship('Task', back_populates='subject', passive_deletes=True)


# Many-to-many for Teacher and Subject
class TeacherSubject(Base):
    # имя таблицы в postgres
    __tablename__ = "teachers_subjects"

    # в таблице не может быть одинаковых совокупностей учитель + предмет
    __table_args__ = (UniqueConstraint('teacher_id', 'subject_id', name='teacher_subject_key'),)

    id = Column(Integer, primary_key=True)
    teacher_id = Column(Integer, ForeignKey('teachers.id', ondelete='CASCADE'), nullable=False)
    subject_id = Column(Integer, ForeignKey('subjects.id', ondelete='CASCADE'), nullable=False)
    # relationship на таблицу Teacher
    teachers = relationship('Teacher', back_populates='teachers_subjects', passive_deletes=True)
    # relationship на таблицу Subject
    subjects = relationship('Subject', back_populates='teachers_subjects', passive_deletes=True)


class Group(Base):
    # имя таблицы в postgres
    __tablename__ = "groups"

    id = Column(Integer, primary_key=True)
    name = Column(String(10), unique=True, nullable=False)
    # relationship на таблицу GroupSubject
    groups_subjects = relationship('GroupSubject', back_populates='group', passive_deletes=True)
    # relationship на таблицу Student
    students = relationship('Student', back_populates='group', passive_deletes=True)
    # relationship на таблицу Task
    tasks = relationship('Task', back_populates='group', passive_deletes=True)


class GroupSubject(Base):
    # имя таблицы в postgres
    __tablename__ = "groups_subjects"

    # в таблице не может быть одинаковых совокупностей группа + предмет
    __table_args__ = (UniqueConstraint('group_id', 'subject_id', name='group_subject_key'),)

    id = Column(Integer, primary_key=True)
    group_id = Column(Integer, ForeignKey('groups.id', ondelete='CASCADE'), nullable=False)
    subject_id = Column(Integer, ForeignKey('subjects.id', ondelete='CASCADE'), nullable=False)
    # relationship на таблицу Group
    group = relationship('Group', back_populates='groups_subjects', passive_deletes=True)
    # relationship на таблицу Subject
    subject = relationship('Subject', back_populates='groups_subjects', passive_deletes=True)


class Task(Base):
    # имя таблицы в postgres
    __tablename__ = "tasks"

    # в таблице не может быть одинаковых совокупностей группа + предмет + название задания
    __table_args__ = (UniqueConstraint('group_id', 'subject_id', 'name', name='task_group_subject_key'),)

    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    description = Column(String(255), nullable=True)
    # foreign keys
    group_id = Column(Integer, ForeignKey('groups.id', ondelete='CASCADE'), nullable=False)
    subject_id = Column(Integer, ForeignKey('subjects.id', ondelete='CASCADE'), nullable=False)
    teacher_id = Column(Integer, ForeignKey('teachers.id', ondelete='CASCADE'), nullable=False)
    # relationships
    group = relationship('Group', back_populates='tasks', passive_deletes=True)
    subject = relationship('Subject', back_populates='tasks', passive_deletes=True)
    teacher = relationship('Teacher', back_populates='tasks', passive_deletes=True)
    # relationship на таблицу File (тк каждый файл должен быть прикреплен к какому-то заданию)
    files = relationship('File', back_populates='task', passive_deletes=True)
    # relationship на таблицу Answer (ответы на задание)
    answers = relationship('Answer', back_populates='task', passive_deletes=True)

class File(Base):
    # имя таблицы в postgres
    __tablename__ = "files"

    id = Column(Integer, primary_key=True)
    code = Column(String(255), nullable=False)
    # Внешний ключ на таблицу Task
    task_id = Column(ForeignKey('tasks.id', ondelete='CASCADE'), nullable=False)
    # relationship на таблицу File (тк каждый файл должен быть прикреплен к какому-то заданию)
    task = relationship('Task', back_populates='files', passive_deletes=True)


class Answer(Base):
    # имя таблицы в postgres
    __tablename__ = "answers"

    id = Column(Integer, primary_key=True)
    description = Column(String(255), nullable=True)
    # foreign keys
    task_id = Column(ForeignKey('tasks.id', ondelete='CASCADE'), nullable=False)
    student_id = Column(ForeignKey('students.id', ondelete='CASCADE'), nullable=False)
    # relationships
    task = relationship('Task', back_populates='answers', passive_deletes=True)
    student = relationship('Student', back_populates='answers', passive_deletes=True)
    # каждый ответ может быть оценен
    mark = relationship('Mark', back_populates='answer', passive_deletes=True)


class Mark(Base):
    # имя таблицы в postgres
    __tablename__ = "marks"

    id = Column(Integer, primary_key=True)
    mark = Column(Integer, primary_key=True)
    description = Column(String(255), nullable=True)
    # foreign key
    answer_id = Column(ForeignKey('answers.id', ondelete='CASCADE'), nullable=False)
    # relationship
    answer = relationship('Answer', back_populates='mark', passive_deletes=True)