from tg_bot.misc.database import Base
from sqlalchemy import Column, Integer, String

class Teacher(Base):
    __tablename__ = "teachers"

    id = Column(Integer, primary_key=True)
    full_name = Column(String(100), nullable=False)
    tg_username = Column(String(100), nullable=False, unique=True)

