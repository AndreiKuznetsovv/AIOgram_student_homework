from aiogram import Dispatcher
from aiogram import types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from tg_bot.misc.states import SelectRole

async def start_command(message: types.Message, state: FSMContext):
    await message.answer(
        text="Здравствуйте, вы преподаватель или студент?",
        reply_markup=None # изменить позже на general клавиатуру
    )
    # Устанавливаем пользователю состояние "выбирает роль"
    await state.set_state(SelectRole.choosing_role)


async def role_chosen(message: types.Message, state: FSMContext):
    if str(message.text.lower()) == "студент":
        # Отчищаем машину состояний в случае, если пользователь студент
        await state.clear()
        await message.answer(
            text="Приветствую вас, дорогой студент!",
            reply_markup=None # изменить позже на student клавиатуру
        )
    elif str(message.text.lower()) == "преподаватель":
        # Устанавливаем пользователю состояние "Преподаватель"
        await state.set_state(SelectRole.teacher)
        await message.answer(
            text="Введите пароль преподавателя."
        )

def register_general(dp: Dispatcher):
    # command handlers
    dp.message.register(start_command, Command('start'))
    # state handlers
    dp.message.register(role_chosen, SelectRole.choosing_role) # Добавить проверку на ContentType