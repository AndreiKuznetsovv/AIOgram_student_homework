from aiogram.fsm.state import StatesGroup, State


# Класс хранения состояний для general handlers (команда start)
class SelectRole(StatesGroup):
    choosing_role = State()


class RegisterTeacher(StatesGroup):
    teacher_password = State()
    teacher_full_name = State()


class RegisterStudent(StatesGroup):
    student_full_name = State()


class TaskInteractionTeacher(StatesGroup):
    teacher = State()
    study_group = State()
    study_subject = State()
    task_name = State()
    description = State()
    upload_file = State()


class TaskInteractionStudent(StatesGroup):
    student = State()
    teacher_full_name = State()
    study_group = State()
    study_subject = State()
    task_name = State()
