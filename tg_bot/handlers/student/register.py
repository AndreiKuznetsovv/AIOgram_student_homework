from aiogram import Dispatcher
from aiogram import types
from aiogram.fsm.context import FSMContext

from tg_bot.misc.database import db_add_func, db_session
from tg_bot.misc.states import TaskInteractionStudent, RegisterStudent
from tg_bot.models.models import Teacher, Student, User


async def check_student_fullname(message: types.Message, state: FSMContext):
    # Проверяем введенное ФИО на наличие 3-ёх слов
    if len(message.text.split()) == 3:
        # переводим full_name в нижний регистр и кладем в словарь MemoryStorage
        await state.update_data(full_name=message.text.lower())
        student_data = await state.get_data()
        # Создаем ОРМ объекты нового пользователя и нового студента
        user_exists = db_session.query(User).filter(User.tg_username == message.from_user.username).first()
        # Проверяем существует ли пользователь с такими данными
        if user_exists:
            new_student = Student(user_id=user_exists.id)
            db_add_func(new_student)
        else:
            new_user = User(full_name=student_data['full_name'], tg_username=student_data['tg_username'])
            db_add_func(new_user)
            new_student = Student(user_id=new_user.id)
            db_add_func(new_student)
        # установка состояния сту
        await state.set_state(TaskInteractionStudent.student)
        # Запишем id преподавателя из базы данных в MemoryStorage
        await state.update_data(student_id=new_student.id)
        # вывод данных на экран для теста
        serialized_answer = ""
        for key, value in student_data.items():
            serialized_answer += f"{key}: {value}\n"
        await message.answer(
            text=f"Студент успешно добавлен!\n"
                 f"{serialized_answer}"
        )
    else:
        # ФИО состоит не из трёх слов
        await message.answer(
            text="ФИО должно состоять из 3-ёх слов"
        )



def register_student(dp: Dispatcher):
    # state handlers
    dp.message.register(check_student_fullname, RegisterStudent.student_full_name)  # Добавить проверку на ContentType
