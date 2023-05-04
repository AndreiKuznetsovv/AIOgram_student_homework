from aiogram import Dispatcher
from aiogram import types
from aiogram.filters import Command


async def test(message: types.Message):
    await message.answer('Hello, teacher!')


def register_teacher(dp: Dispatcher):
    dp.message.register(test, Command('test_teacher'))