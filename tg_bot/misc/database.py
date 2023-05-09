from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.exc import SQLAlchemyError


db_engine = create_engine('postgresql://dron_test:2805@localhost/students_homework')
db_session = scoped_session(
    sessionmaker(autocommit=False, autoflush=False, bind=db_engine)
)

Base = declarative_base()
Base.query = db_session.query_property()

def db_init():
    from tg_bot.models import models
    Base.metadata.create_all(bind=db_engine)


def db_commit_func() -> bool:
    try:
        db_session.commit()
        return True
    except SQLAlchemyError:
        db_session.rollback()
        return False


def db_add_func(data: Base) -> bool:
    try:
        db_session.add(data)
    except SQLAlchemyError:
        db_session.rollback()
        return False
    # если session.add отработала, то необходимо закоммитить изменения
    return db_commit_func()


def db_delete_func(data: Base) -> bool:
    try:
        db_session.delete(data)
    except SQLAlchemyError:
        db_session.rollback()
        return False
    # если session.delete отработала, то необходимо закоммитить изменения
    return db_commit_func()