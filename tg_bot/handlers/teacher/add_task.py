from aiogram import Dispatcher, F
from aiogram import types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import ReplyKeyboardRemove

from tg_bot.keyboards.reply.general import reply_cancel_kb
from tg_bot.misc.database import db_add_func, db_session
from tg_bot.misc.states import AddTaskTeacher, SelectRole
from tg_bot.models.models import (
    Task, File, Group,
    Subject, GroupSubject, TeacherSubject,
    TaskFile,
)


async def request_subject(message: types.Message, state: FSMContext):
    # установим состояние и запросим название предмета
    await state.set_state(AddTaskTeacher.study_subject)
    await message.answer(
        text="Введите название предмета, по которому хотите добавить задание.",
        reply_markup=ReplyKeyboardRemove()
    )


async def request_group(message: types.Message, state: FSMContext):
    # запишем название предмета в MemoryStorage
    await state.update_data(subject_name=message.text.lower())
    # установим состояние и запросим название группы
    await state.set_state(AddTaskTeacher.study_group)
    await message.answer(
        text="Введите название группы, для которой вы хотите добавить задание.",
        reply_markup=None
    )


async def request_task_name(message: types.Message, state: FSMContext):
    if len(message.text.split('-')) == 2:
        # запишем название группы в MemoryStorage
        await state.update_data(group_name=message.text.lower())
        # установим состояние и запросим название задания
        await state.set_state(AddTaskTeacher.task_name)
        await message.answer(
            text="Введите название задания.",
        )
        # если название группы было введено некорректно
    else:
        await message.answer(
            text="Вы ввели неверное название группы.\n"
                 "Оно должно состоять из 2-ух словах, разделенных тире.\n"
                 "Попробуйте еще раз."
        )


async def request_description(message: types.Message, state: FSMContext):
    # Запишем название предмета в MemoryStorage
    await state.update_data(task_name=message.text.lower())

    # Установим состояние и запросим описание задания
    await state.set_state(AddTaskTeacher.description)
    await message.answer(
        text="Введите описание задания."
    )


async def upload_subject(state: FSMContext):
    data = await state.get_data()
    # проверим, существует ли такой предмет (если нет - добавим)
    subject = db_session.query(Subject).filter_by(name=data['subject_name']).first()
    if not subject:
        subject = Subject(name=data['subject_name'])
        db_add_func(subject)
    # Добавим в MemoryStorage id предмета
    await state.update_data(subject_id=subject.id)

    # Добавим отношение учитель - предмет
    teacher_subject = TeacherSubject(teacher_id=data['teacher_id'], subject_id=subject.id)
    db_add_func(teacher_subject)


async def upload_group(state: FSMContext):
    data = await state.get_data()
    # проверим, существует ли такая группа (если нет - добавим)
    group = db_session.query(Group).filter_by(name=data['group_name']).first()
    if not group:
        group = Group(name=data['group_name'])
        db_add_func(group)
    # Добавим в MemoryStorage id группы
    await state.update_data(group_id=group.id)

    # добавим отношение - группа предмет
    group_subject = GroupSubject(group_id=group.id, subject_id=data['subject_id'])
    db_add_func(group_subject)


async def upload_task(message: types.Message, state: FSMContext):
    # Загрузим в БД введенный предмет, чтобы добавить задание по нему
    await upload_subject(state)
    # Загрузим в БЖ веденную группу, чтобы добавить задание для неё
    await upload_group(state)

    # Запишем описание задания в MemoryStorage
    await state.update_data(description=message.text)

    # Получим все данные из MemoryStorage
    task_data = await state.get_data()

    # Создадим новый объект класса Task и сохраним его в БД
    new_task = Task(
        subject_id=task_data['subject_id'],
        group_id=task_data['group_id'],
        teacher_id=task_data['teacher_id'],
        name=task_data['task_name'],
        description=task_data['description'],
    )
    db_add_func(new_task)

    # загрузим task_id в MemoryStorage, чтобы указать к какому заданию прикрепляются файлы
    await state.update_data(task_id=new_task.id)

    # Установим состояние и запросим добавление файлов
    await state.set_state(AddTaskTeacher.upload_file)
    await message.answer(
        text='Задание успешно добавлено!\n'
             'Теперь добавьте файлы к заданию.\n'
             'Или введите команду /cancel чтобы не добавлять файлы',
        reply_markup=reply_cancel_kb()
    )


async def upload_files(message: types.Message, state: FSMContext):
    # Получим все данные из MemoryStorage
    task_data = await state.get_data()

    # Добавим файл в БД (с проверкой на расширение файла)
    try:
        new_file = File(code=message.document.file_id)
        db_add_func(new_file)
        new_task_file = TaskFile(file_id=new_file.id, task_id=task_data['task_id'])
        db_add_func(new_task_file)
    except AttributeError:
        await message.answer(
            text="Файл с данным расширением добавить невозможно.\n"
                 "Если вы хотите загрузить изображение, уберите галочку с \"Сжать изображение\""
        )
        return
    db_add_func(new_file)

    # Проинструктируем преподавателя
    await message.answer(
        text='Файл успешно добавлен!\n'
             'Вы можете продолжить добавление файлов!\n'
             'Или ввести команду /cancel чтобы закончить добавление файлов.',
        reply_markup=reply_cancel_kb()
    )


def register_teacher_add_task(dp: Dispatcher):
    # state handlers
    dp.message.register(request_subject, Command('add_task', ignore_case=True),
                        SelectRole.teacher)
    dp.message.register(request_group, AddTaskTeacher.study_subject)
    dp.message.register(request_task_name, AddTaskTeacher.study_group)
    dp.message.register(request_description, AddTaskTeacher.task_name)
    dp.message.register(upload_task, AddTaskTeacher.description)
    dp.message.register(upload_files, AddTaskTeacher.upload_file, F.document)
