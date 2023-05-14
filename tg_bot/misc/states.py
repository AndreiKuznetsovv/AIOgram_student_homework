from aiogram.fsm.state import StatesGroup, State


# Класс хранения состояний для general handlers (команда start)
class SelectRole(StatesGroup):
    choosing_role = State()


class RegisterTeacher(StatesGroup):
    teacher_password = State()
    teacher_full_name = State()


class RegisterStudent(StatesGroup):
    student_full_name = State()
    student_study_group = State()


class TaskInteractionTeacher(StatesGroup):
    teacher = State()
    study_subject = State()
    study_group = State()
    task_name = State()
    description = State()
    upload_file = State()


class TaskInteractionStudent(StatesGroup):
    student = State()
    study_subject = State()
    teacher_full_name = State()
    task_name = State()
