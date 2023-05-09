from aiogram import Dispatcher
from aiogram import types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from tg_bot.config import load_config
from tg_bot.misc.states import RegisterTeacher, SelectRole

from tg_bot.models.models import Teacher
from tg_bot.misc.database import db_add_func

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


async def check_teacher_fullname(message: types.Message, state: FSMContext):
    # Проверяем введенное ФИО на наличие 3-ёх слов
    if len(message.text.split()) == 3:
        # кладём full_name преподавателя в словарь MemoryStorage
        await state.update_data(full_name=message.text)
        await message.answer(
            text="Введите telegram username преподавателя",
            reply_markup=None  # Позже заменить на kb_inline_back (для перехода на шаг назад)
        )
        # Устанавливаем состояние пользователю "Ввести tg username"
        await state.set_state(RegisterTeacher.teacher_tg_username)
    else:
        # ФИО состоит не из трёх слов
        await message.answer(
            text="ФИО должно состоять из 3-ёх слов"
        )


async def check_teacher_username(message: types.Message, state: FSMContext):
    # Добавить проверку занят ли такой юзернейм
    await state.update_data(username=message.text.replace("@", ""))
    teacher_data = await state.get_data()
    # Добавить отправку данных в БД
    teacher = Teacher(full_name=teacher_data['full_name'], tg_username=teacher_data['username'])
    db_add_func(teacher)
    # вывод данных на экран для теста
    serialized_answer = ""
    for key, value in teacher_data.items():
        serialized_answer += f"{key}: {value}\n"
    await message.answer(
        text=f"{serialized_answer}"
    )



def register_teacher(dp: Dispatcher):
    # command handlers
    dp.message.register(test, Command('test_teacher'))
    # state handlers
    dp.message.register(check_teacher_password, SelectRole.teacher)  # Добавить проверку на ContentType
    dp.message.register(check_teacher_fullname, RegisterTeacher.teacher_full_name)  # Добавить проверку на ContentType
    dp.message.register(check_teacher_username, RegisterTeacher.teacher_tg_username) # Добавить проверку на ContentType
