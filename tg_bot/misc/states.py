from aiogram.fsm.state import StatesGroup, State


# Класс хранения состояний для general handlers (команда start)
class SelectRole(StatesGroup):
    choosing_role = State()
    teacher = State()


# Класс хранения состояний для регистрации преподавателя
class RegisterTeacher(StatesGroup):
    teacher_full_name = State()
    teacher_tg_username = State()

