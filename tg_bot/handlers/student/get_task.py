from aiogram import Dispatcher
from aiogram import types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from tg_bot.keyboards.reply import create_cancel_keyboard
from tg_bot.misc.database import db_session
from tg_bot.misc.states import GetTaskStudent, SelectRole
from tg_bot.models.models import (
    Task, File, Teacher,
    User, GroupSubject, Subject,
    TeacherSubject, TaskFile,
)


async def select_subject(message: types.Message, state: FSMContext):
    # Установим состояние и запросим название предмета
    await state.set_state(GetTaskStudent.study_subject)
    await message.answer(
        text="Введите название предмета.",
        reply_markup=create_cancel_keyboard()
    )


async def select_teacher(message: types.Message, state: FSMContext):
    # Получим данные из MemoryStorage, чтобы получить group_id студента
    data = await state.get_data()

    # Проверим, есть ли задания по данному предмету для группы, в которой обучается студент
    subject_group = db_session.query(GroupSubject).join(Subject).filter(
        Subject.name == message.text.lower(),
        GroupSubject.group_id == data['group_id']
    ).first()
    if subject_group:
        # Добавим в MemoryStorage id предмета
        await state.update_data(subject_id=subject_group.subject_id)

        # Установим состояние и запросим ФИО преподавателя
        await state.set_state(GetTaskStudent.teacher_full_name)
        await message.answer(
            text="Введите ФИО преподавателя."
        )
    else:
        await message.answer(
            text="Такого предмета не существует\n"
                 "или заданий для вашей группы по данному предмету нет.\n"
                 "Попробуйте ввести название предмета еще раз."
        )


async def select_task_name(message: types.Message, state: FSMContext):
    # Проверяем введенное ФИО на наличие 3-ёх слов
    if len(message.text.split()) == 3:
        # Получим данные из MemoryStorage, чтобы получить subject_id
        data = await state.get_data()

        # Проверим, преподает ли данный преподаватель выбранный предмет
        teacher = db_session.query(Teacher).join(User).join(TeacherSubject).filter(
            User.full_name == message.text.lower(),
            TeacherSubject.subject_id == data['subject_id']
        ).first()
        if teacher:
            # Добавим в MemoryStorage id преподавателя
            await state.update_data(teacher_id=teacher.id)

            # установим состояние и запросим название задания
            await state.set_state(GetTaskStudent.task_name)
            await message.answer(
                text="Введите название задания.",
                reply_markup=create_cancel_keyboard()  # Добавить клавиатуру для выбора группы
            )
        else:
            await message.answer(
                text="Преподавателя с таким ФИО не существует\n"
                     "или он не добавил заданий по выбранному предмету.\n"
                     "Попробуйте ввести ФИО преподавателя еще раз."
            )
    else:
        # ФИО состоит не из трёх слов
        await message.answer(
            text="ФИО должно состоять из 3-ёх слов"
        )


async def show_selected_task(message: types.Message, state: FSMContext):
    # Добавим в MemoryStorage название задания
    await state.update_data(task_name=message.text.lower())

    # Получим из MemoryStorage данные о задании
    task_data = await state.get_data()

    # получим выбранное задание из БД
    selected_task = db_session.query(Task).filter_by(
        group_id=task_data['group_id'],
        subject_id=task_data['subject_id'],
        teacher_id=task_data['teacher_id'],
        name=task_data['task_name'],
    ).first()

    # получим прикрепленные к заданию файлы
    task_files = db_session.query(File).join(TaskFile).filter(TaskFile.task_id == selected_task.id).all()

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


def register_student_select_task(dp: Dispatcher):
    # Command handlers
    dp.message.register(select_subject, Command('select_task', ignore_case=True), SelectRole.student)
    # state handlers
    dp.message.register(select_teacher, GetTaskStudent.study_subject)
    dp.message.register(select_task_name, GetTaskStudent.teacher_full_name)
    dp.message.register(show_selected_task, GetTaskStudent.task_name)
