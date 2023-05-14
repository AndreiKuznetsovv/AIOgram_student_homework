from aiogram import Dispatcher
from aiogram import types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from tg_bot.config import load_config
from tg_bot.misc.database import db_add_func, db_session
from tg_bot.misc.states import RegisterTeacher, SelectRole, TaskInteractionTeacher
from tg_bot.models.models import Teacher, User

# перенести работу с конфигом в middleware позже
config = load_config(".env")


async def test(message: types.Message):
    await message.answer('Здравствуйте, учитель!')


async def check_teacher_password(message: types.Message, state: FSMContext):
    # Проверяем корректность пароля преподавателя
    if str(message.text.lower()) == config.tg_bot.teacher_password:
        await message.answer(
            text="Введите ФИО преподавателя."
        )
        # Устанавливаем пользователю состояние"ввести ФИО"
        await state.set_state(RegisterTeacher.teacher_full_name)
    else:
        # Пароль введен неверно, пользователю предлагается ввести его снова.
        await message.answer(
            text="Вы ввели неверный пароль. Попробуйте еще раз."
        )


async def upload_teacher(message: types.Message, state: FSMContext):
    # Проверяем введенное ФИО на наличие 3-ёх слов
    if len(message.text.split()) == 3:
        # Добавим в MemoryStorage id ФИО преподавателя
        await state.update_data(full_name=message.text.lower())

        # Получим данные об учителе из MemoryStorage
        teacher_data = await state.get_data()

        # Создаем ОРМ объекты нового пользователя и нового студента
        user_exists = db_session.query(User).filter(User.tg_username == message.from_user.username).first()

        # Проверяем существует ли пользователь с такими данными
        if user_exists:
            # Создаем нового преподавателя
            new_teacher = Teacher(user_id=user_exists.id)
            db_add_func(new_teacher)
        else:
            # создаем нового пользователя и нового преподавателя
            new_user = User(full_name=teacher_data['full_name'], tg_username=teacher_data['tg_username'])
            db_add_func(new_user)
            new_teacher = Teacher(user_id=new_user.id)
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
    else:
        # ФИО состоит не из трёх слов
        await message.answer(
            text="ФИО должно состоять из 3-ёх слов"
        )


def register_teacher(dp: Dispatcher):
    # command handlers
    dp.message.register(test, Command('test_teacher'))
    # state handlers
    dp.message.register(check_teacher_password, RegisterTeacher.teacher_password)  # Добавить проверку на ContentType
    dp.message.register(upload_teacher, RegisterTeacher.teacher_full_name)  # Добавить проверку на ContentType
