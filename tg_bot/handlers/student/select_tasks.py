from aiogram import Dispatcher
from aiogram import types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from tg_bot.misc.database import db_session
from tg_bot.misc.states import TaskInteractionStudent
from tg_bot.models.models import Task, File, Teacher


async def test(message: types.Message):
    await message.answer('Здравствуйте, студент')


async def select_teacher(message: types.Message, state: FSMContext):
    await message.answer(
        text="Введите ФИО преподавателя"
    )
    await state.set_state(TaskInteractionStudent.teacher_full_name)


async def select_group(message: types.Message, state: FSMContext):
    # Проверяем введенное ФИО на наличие 3-ёх слов
    if len(message.text.split()) == 3:
        # проверяем существует ли такое ФИО в БД
        teacher = db_session.query(Teacher).filter(Teacher.full_name == message.text.lower().strip()).first()
        if teacher:
            # Добавим в MemoryStorage ФИО преподавателя и его id в БД
            await state.update_data(teacher_id=teacher.id)
            await message.answer(
                text="Введите название группы, задания которой хотите получить."
            )
            await state.set_state(TaskInteractionStudent.study_group)
        else:
            await message.answer(
                text="Преподавателя с таким ФИО не существует.\n"
                     "Попробуйте еще раз."
            )
    else:
        # ФИО состоит не из трёх слов
        await message.answer(
            text="ФИО должно состоять из 3-ёх слов"
        )


async def select_subject(message: types.Message, state: FSMContext):
    # позже завести отдельную таблицу для групп и добавить проверку на существование группы
    if len(message.text.split('-')) == 2:
        await state.update_data(study_group=message.text.lower().strip())
        await message.answer(
            text="Введите название предмета.",
            reply_markup=None
        )
        await state.set_state(TaskInteractionStudent.study_subject)
    else:
        await message.answer(
            text="Вы ввели неверное название группы.\n"
                 "Оно должно состоять из 2-ух словах, разделенных тире.\n"
                 "Попробуйте еще раз."
        )


async def select_task_name(message: types.Message, state: FSMContext):
    await state.update_data(study_subject=message.text.strip().lower())
    await message.answer(
        text="Введите название задания."
    )
    await state.set_state(TaskInteractionStudent.task_name)


async def show_selected_task(message: types.Message, state: FSMContext):
    await state.update_data(task_name=message.text.strip().lower())
    task_data = await state.get_data()
    # получим выбранное задание из БД
    selected_task = db_session.query(Task).filter_by(
        group=task_data['study_group'],
        subject=task_data['study_subject'],
        task_name=task_data['task_name'],
        teacher_id=task_data['teacher_id']
    ).first()
    # получим прикрепленные к заданию файлы
    task_files = db_session.query(File).filter_by(task_id=selected_task.id).all()
    # если файлов > 1 отправляем группу документов, иначе 1 документ
    if len(task_files) > 1:
        # преобразуем полученный список объектов класса File в список документов
        media_list = [types.InputMediaDocument(media=file.code) for file in task_files]
        await message.answer_media_group(media=media_list)
        await message.answer(
            text=f"Описание работы: {selected_task.description}"
        )
    else:
        await message.answer_document(
            document=task_files[0].code,
            caption=f"Описание работы: {selected_task.description}"
        )
    # очистим состояние пользователя
    await state.clear()


def register_student(dp: Dispatcher):
    # Command handlers
    dp.message.register(test, Command('test_student'))
    # state handlers
    dp.message.register(select_teacher, TaskInteractionStudent.student, Command('select_task'))
    dp.message.register(select_group, TaskInteractionStudent.teacher_full_name)
    dp.message.register(select_subject, TaskInteractionStudent.study_group)
    dp.message.register(select_task_name, TaskInteractionStudent.study_subject)
    dp.message.register(show_selected_task, TaskInteractionStudent.task_name)
