from aiogram.fsm.state import StatesGroup, State


# Класс хранения состояний для general handlers (команда start)
class SelectRole(StatesGroup):
    choosing_role = State()
    teacher = State()
    student = State()


'''
Teacher StateGroup classes
'''


class RegisterTeacher(StatesGroup):
    teacher_password = State()
    teacher_full_name = State()


class AddTaskTeacher(StatesGroup):
    study_subject = State()
    study_group = State()
    task_name = State()
    description = State()
    upload_file = State()


class GetAnswersTeacher(StatesGroup):
    study_subject = State()
    study_group = State()
    task_name = State()


class RateAnswerTeacher(StatesGroup):
    student_name = State()
    rate_answer = State()
    description = State()


'''
Student StateGroup classes
'''


class RegisterStudent(StatesGroup):
    student_full_name = State()
    student_study_group = State()


class GetTaskStudent(StatesGroup):
    study_subject = State()
    teacher_full_name = State()
    task_name = State()


class SendAnswerStudent(StatesGroup):
    study_subject = State()
    teacher_full_name = State()
    task_name = State()
    description = State()
    upload_file = State()
