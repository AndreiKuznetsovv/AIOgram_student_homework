from aiogram import Dispatcher
from aiogram import types
from aiogram.filters import Command, Text
from aiogram.fsm.context import FSMContext

from tg_bot.keyboards.reply import (
    create_general_kb,
    create_student_select_kb,
    create_teacher_add_kb,
)
from tg_bot.misc.database import db_session
from tg_bot.misc.states import SelectRole, TaskInteractionTeacher, TaskInteractionStudent, RegisterTeacher, RegisterStudent
from tg_bot.models.models import Teacher, Student, User

'''
В данном файле будут описаны:
**Старт диалога с пользователем /start
**Вспомогательная команда /help (пока не реализована)
'''


async def start_command(message: types.Message, state: FSMContext):
    await message.answer(
        text="Здравствуйте, вы преподаватель или студент?",
        reply_markup=create_general_kb()
    )
    # Устанавливаем пользователю состояние "выбирает роль"
    await state.set_state(SelectRole.choosing_role)


async def student_role(message: types.Message, state: FSMContext):
    # Проверим, существует ли студент с username'ом пользователя, который выбирает роль
    student = db_session.query(Student).join(User).filter(User.tg_username == message.from_user.username).first()
    if student:
        await message.answer(
            text='Вы уже зарегистрированы как студент.\n'
                 'Можете переходить к работе с заданиями.',
            reply_markup=None # Заменить позже на student клавиатуру
        )
        # Установить состояние "преподаватель" чтобы преподаватель мог работать с заданиями
        await state.set_state(TaskInteractionStudent.student)
        # Запишем id преподавателя из базы данных в MemoryStorage
        await state.update_data(student_id=student.id)
    else:
        # Устанавливаем пользователю состояние регистрации нового преподавателя
        await state.set_state(RegisterStudent.student_full_name)
        # поместим tg_username в MemoryStorage (понадобится в дальнейшем для регистрации)
        await state.update_data(tg_username=message.from_user.username)
        await message.answer(
            text="Введите полное ФИО студента."
        )


async def teacher_role(message: types.Message, state: FSMContext):
    # Проверим, существует ли преподаватель с username'ом пользователя, который выбирает роль
    teacher = db_session.query(Teacher).join(User).filter(User.tg_username == message.from_user.username).first()
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
        # Устанавливаем пользователю состояние регистрации нового преподавателя
        await state.set_state(RegisterTeacher.teacher_password)
        # поместим tg_username в MemoryStorage (понадобится в дальнейшем для регистрации)
        await state.update_data(tg_username=message.from_user.username)
        await message.answer(
            text="Введите пароль преподавателя."
        )


async def command_cancel(message: types.Message, state: FSMContext):
    """
    Позволяет пользователю отменить любое действие
    """
    current_state = await state.get_state()
    if current_state is None:
        return

    await state.clear()
    await message.reply('Отмена произошла успешно!')


def register_general(dp: Dispatcher):
    # cancel handler
    dp.message.register(command_cancel, Command('cancel'), )
    # command handlers
    dp.message.register(start_command, Command('start', ignore_case=True))
    # state handlers
    dp.message.register(student_role, SelectRole.choosing_role,
                        Text(text=('Студент', 'студент')))  # Добавить проверку на ContentType
    dp.message.register(teacher_role, SelectRole.choosing_role,
                        Text(text=('Преподаватель', 'преподаватель')))  # Добавить проверку на ContentType
