from aiogram import types
from aiogram.utils.keyboard import ReplyKeyboardBuilder

def reply_teacher_kb():
    # создаем объект сборщика
    builder = ReplyKeyboardBuilder()
    # добавляем 2 кнопки
    builder.add(types.KeyboardButton(text='/add_task'))
    builder.add(types.KeyboardButton(text='/get_answers'))
    # устанавливаем кол-во кнопок в ряду
    builder.adjust(1)
    # возвращаем клавиатуру
    return builder.as_markup(resize_keyboard=True, one_time_keyboard=True)