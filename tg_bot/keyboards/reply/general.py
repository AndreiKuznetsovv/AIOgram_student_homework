from aiogram import types
from aiogram.utils.keyboard import ReplyKeyboardBuilder

def reply_start_kb():
    # создаем объект сборщика
    builder = ReplyKeyboardBuilder()
    # добавляем 2 кнопки
    builder.add(types.KeyboardButton(text='Студент'))
    builder.add(types.KeyboardButton(text='Преподаватель'))
    # устанавливаем кол-во кнопок в ряду
    builder.adjust(2)
    # возвращаем клавиатуру
    return builder.as_markup(resize_keyboard=True)

def reply_cancel_kb():
    # создаем объект сборщика
    builder = ReplyKeyboardBuilder()
    # добавляем 2 кнопки
    builder.add(types.KeyboardButton(text='/cancel'))
    # устанавливаем кол-во кнопок в ряду
    builder.adjust(1)
    # возвращаем клавиатуру
    return builder.as_markup(resize_keyboard=True)