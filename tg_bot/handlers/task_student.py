from aiogram import Dispatcher
from aiogram import types
from aiogram.filters import Command

async def test(message: types.Message):
    await message.answer('Здравствуйте, студент')



def register_student(dp: Dispatcher):
    # Command handlers
    dp.message.register(test, Command('test_student'))
    # state handlers
    # dp.message.register()