from aiogram import Dispatcher
from aiogram import types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from tg_bot.config import load_config
from tg_bot.misc.database import db_add_func, db_session
from tg_bot.misc.states import RegisterTeacher, SelectRole, TaskInteractionTeacher
from tg_bot.models.models import Teacher

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
        # переводим full_name в нижний регистр и кладем в словарь MemoryStorage
        await state.update_data(full_name=message.text.lower())
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


async def upload_teacher(message: types.Message, state: FSMContext):
    username = message.text.replace("@", "")
    teacher = db_session.query(Teacher).filter(Teacher.tg_username == username).first()
    if teacher:
        await message.answer(
            text="Преподаватель с таким telegram username уже зарегистрирован!\n"
                 "Войдите в telegram аккаунт преподавателя для работы с заданиями"
        )
        # обнуление состояния пользователя
        await state.clear()
    else:
        await state.update_data(username=username)
        teacher_data = await state.get_data()
        new_teacher = Teacher(full_name=teacher_data['full_name'], tg_username=teacher_data['username'])
        db_add_func(new_teacher)
        # установка состояния преподавателя
        await state.set_state(TaskInteractionTeacher.teacher)
        # Запишем id преподавателя из базы данных в MemoryStorage
        await state.update_data(teacher_id=new_teacher.id)
        # вывод данных на экран для теста
        serialized_answer = ""
        for key, value in teacher_data.items():
            serialized_answer += f"{key}: {value}\n"
        await message.answer(
            text=f"Преподаватель успешно добавлен!\n"
                 f"{serialized_answer}"
        )


def register_teacher(dp: Dispatcher):
    # command handlers
    dp.message.register(test, Command('test_teacher'))
    # state handlers
    dp.message.register(check_teacher_password, SelectRole.teacher)  # Добавить проверку на ContentType
    dp.message.register(check_teacher_fullname, RegisterTeacher.teacher_full_name)  # Добавить проверку на ContentType
    dp.message.register(upload_teacher, RegisterTeacher.teacher_tg_username)  # Добавить проверку на ContentType
