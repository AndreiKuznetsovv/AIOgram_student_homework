from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


def create_general_kb():
    b1 = KeyboardButton(text="Студент")
    b2 = KeyboardButton(text="Преподаватель")
    # Добавить кнопку /help
    # возможно переписать на ReplyKeyboardBuilder
    general_kb = ReplyKeyboardMarkup(
        keyboard=[[b1, b2]],
        resize_keyboard=True,
        input_field_placeholder='Выберите роль'
    )
    return general_kb


def create_student_select_kb():
    select_button = KeyboardButton(text="/select_task")

    student_select_kb = ReplyKeyboardMarkup(
        keyboard=[[select_button]],
        resize_keyboard=True,
        input_field_placeholder='Выберите действие'
    )
    return student_select_kb


def create_teacher_add_kb():
    add_button = KeyboardButton(text="/add_task")
    cancel_button = KeyboardButton(text="/cancel")

    student_select_kb = ReplyKeyboardMarkup(
        keyboard=[[add_button, cancel_button]],
        resize_keyboard=True,
        input_field_placeholder='Выберите действие'
    )
    return student_select_kb

def create_cancel_keyboard():
    cancel_button = KeyboardButton(text="/cancel")

    student_select_kb = ReplyKeyboardMarkup(
        keyboard=[[cancel_button]],
        resize_keyboard=True,
        input_field_placeholder='Для отмены нажмите /cancel',
        one_time_keyboard=True
    )
    return student_select_kb