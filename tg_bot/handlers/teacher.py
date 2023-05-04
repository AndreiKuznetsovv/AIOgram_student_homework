from aiogram import Dispatcher
from aiogram import types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from tg_bot.config import load_config
from tg_bot.misc.states import RegisterTeacher, SelectRole

# перенести работу с конфигом в middleware позже
config = load_config(".env")


async def test(message: types.Message):
    await message.answer('Здравствуйте, учитель!')


async def check_teacher_password(message: types.Message, state: FSMContext):
    # Проверяем корректность пароля преподавателя
    if str(message.text.lower()) == config.tg_bot.teacher_password:
        await message.answer(
            text="Введите полное ФИО преподавателя."
        )
        # Устанавливаем пользователю состояние"ввести ФИО"
        await state.set_state(RegisterTeacher.teacher_full_name)
    else:
        # Пароль введен неверно, пользователю предлагается ввести его снова.
        await message.answer(
            text="Вы ввели неверный пароль. Попробуйте еще раз."
        )


def register_teacher(dp: Dispatcher):
    # command handlers
    dp.message.register(test, Command('test_teacher'))
    # state handlers
    dp.message.register(check_teacher_password, SelectRole.teacher)
