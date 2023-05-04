from aiogram import Dispatcher
from aiogram import types
from aiogram.filters import Command

async def test(message: types.Message):
    await message.answer('Hello, student!')


def register_student(dp: Dispatcher):
    dp.message.register(test, Command('test_student'))