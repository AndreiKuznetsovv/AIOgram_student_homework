from aiogram import Dispatcher
from aiogram import types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from tg_bot.misc.database import db_session
from tg_bot.misc.states import SelectRole, TaskInteractionTeacher, TaskInteractionStudent
from tg_bot.models.models import Teacher


async def start_command(message: types.Message, state: FSMContext):
    await message.answer(
        text="Здравствуйте, вы преподаватель или студент?",
        reply_markup=None  # изменить позже на general клавиатуру
    )
    # Устанавливаем пользователю состояние "выбирает роль"
    await state.set_state(SelectRole.choosing_role)


async def role_chosen(message: types.Message, state: FSMContext):
    if str(message.text.lower()) == "студент":
        # Отчищаем машину состояний в случае, если пользователь студент
        await state.clear()
        await message.answer(
            text="Приветствую вас, дорогой студент!",
            reply_markup=None  # изменить позже на student клавиатуру
        )
        await state.set_state(TaskInteractionStudent.student)
    elif str(message.text.lower()) == "преподаватель":
        teacher = db_session.query(Teacher).filter(Teacher.tg_username == message.from_user.username).first()
        if teacher:
            await message.answer(
                text='Вы уже зарегистрированы как преподаватель.\n'
                     'Можете переходить к работе с заданиями.',
                reply_markup=None  # Заменить позже на teacher клавиатуру
            )
            # Установить состояние "преподаватель" чтобы преподаватель мог работать с заданиями
            await state.set_state(TaskInteractionTeacher.teacher)
            # Запишем id преподавателя из базы данных в MemoryStorage
            await state.update_data(teacher_id=teacher.id)
        else:
            # Устанавливаем пользователю состояние "Преподаватель"
            await state.set_state(SelectRole.teacher)
            await message.answer(
                text="Введите пароль преподавателя."
            )


def register_general(dp: Dispatcher):
    # command handlers
    dp.message.register(start_command, Command('start'))
    # state handlers
    dp.message.register(role_chosen, SelectRole.choosing_role)  # Добавить проверку на ContentType
