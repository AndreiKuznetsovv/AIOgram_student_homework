from aiogram import types
from aiogram.utils.keyboard import ReplyKeyboardBuilder

def reply_student_kb():
    # создаем объект сборщика
    builder = ReplyKeyboardBuilder()
    # добавляем 2 кнопки
    builder.add(types.KeyboardButton(text='/get_task'))
    builder.add(types.KeyboardButton(text='/get_marks'))
    builder.add(types.KeyboardButton(text='/send_answer'))
    # устанавливаем кол-во кнопок в ряду
    builder.adjust(2)
    # возвращаем клавиатуру
    return builder.as_markup(resize_keyboard=True, one_time_keyboard=True)
