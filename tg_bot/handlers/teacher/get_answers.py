from collections import Counter

from aiogram import Dispatcher
from aiogram import types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from tg_bot.keyboards.reply import create_cancel_keyboard
from tg_bot.misc.database import db_session
from tg_bot.misc.states import SelectRole, GetAnswersTeacher, RateAnswerTeacher
from tg_bot.models.models import (
    Task, Subject,
    TeacherSubject, Group, GroupSubject, )


async def select_subject(message: types.Message, state: FSMContext):
    # Установим состояние и запросим название предмета
    await state.set_state(GetAnswersTeacher.study_subject)
    await message.answer(
        text="Введите название предмета.",
        reply_markup=create_cancel_keyboard()
    )


async def select_group(message: types.Message, state: FSMContext):
    # Получим данные из MemoryStorage, чтобы получить teacher_id учителя
    data = await state.get_data()

    # проверим, существует ли такой предмет
    subject = db_session.query(Subject).join(TeacherSubject).filter(
        Subject.name == message.text.lower(),
        TeacherSubject.teacher_id == data['teacher_id']
    ).first()
    if subject:
        # Добавим в MemoryStorage id предмета
        await state.update_data(subject_id=subject.id)

        # установим состояние и запросим название группы
        await state.set_state(GetAnswersTeacher.study_group)
        await message.answer(
            text="Введите название группы, ответы которой вы хотите получить.",
            reply_markup=create_cancel_keyboard()
        )
    else:
        await message.answer(
            text="Такого предмета не существует\n"
                 "или вы не добавляли заданий по данному предмету.\n"
                 "Попробуйте ввести название предмета еще раз."
        )


async def select_task_name(message: types.Message, state: FSMContext):
    if len(message.text.split('-')) == 2:
        # Получим данные из MemoryStorage, чтобы получить subject_id учителя
        data = await state.get_data()

        # проверим, существует ли такая группа
        group = db_session.query(Group).join(GroupSubject).filter(
            Group.name == message.text.lower(),
            GroupSubject.subject_id == data['subject_id']
        ).first()
        if group:
            # Добавим в MemoryStorage id группы
            await state.update_data(group_id=group.id)

            # установим состояние и запросим название задания
            await state.set_state(GetAnswersTeacher.task_name)
            await message.answer(
                text="Введите название задания, ответы на которое вы хотите получить.",
            )
        else:
            await message.answer(
                text="Такой группы не существует\n"
                     "или вы не добавляли заданий по данному предмету для данной группы.\n"
                     "Попробуйте ввести название группы еще раз."
            )
        # если название группы было введено некорректно
    else:
        await message.answer(
            text="Вы ввели неверное название группы.\n"
                 "Оно должно состоять из 2-ух словах, разделенных тире.\n"
                 "Попробуйте еще раз."
        )


async def show_all_answers(message: types.Message, state: FSMContext):
    # Добавим в MemoryStorage название задания
    await state.update_data(task_name=message.text.lower())

    # Получим из MemoryStorage данные о задании
    task_data = await state.get_data()
    try:
        # получим выбранные ответы на задание из БД
        answers = db_session.query(Task).filter_by(
            group_id=task_data['group_id'],
            subject_id=task_data['subject_id'],
            teacher_id=task_data['teacher_id'],
            name=task_data['task_name'],
        ).first().answers
    except AttributeError:
        await message.answer(
            text="Задания с таким названием не существует.\n"
                 "Попробуйте еще раз."
        )
        return

    # Запишем ответы в MemoryStorage
    await state.update_data(answers=answers)
    # Получим ФИО тех, кто прислал ответ и отправим преподавателю
    students_ids_names = {str(answer.student.id): answer.student.user.full_name for answer in answers}
    # Запишем полученный словарь в MemoryStorage
    await state.update_data(students_ids_names=students_ids_names)

    serialized_answer = "Список студентов, которые отправили ответ, в формате\n" \
                        "ФИО студента: количество отправленных ответов\n" \
                        "----------------------------------------------------------------------------\n"
    for full_name, count in Counter([answer.student.user.full_name for answer in answers]).items():
        serialized_answer += f"{full_name}: {count}\n"
    await message.answer(
        text=f"{serialized_answer}"
    )

    # Установим состояние пользователю и запросим ввести ФИО студента
    await state.set_state(RateAnswerTeacher.student_name)
    await message.answer(
        text="Введите ФИО студента, чьи ответы хотите оценить."
    )


def register_teacher_get_answers(dp: Dispatcher):
    # Command handlers
    dp.message.register(select_subject, Command('get_answers', ignore_case=True), SelectRole.teacher)
    # state handlers
    dp.message.register(select_group, GetAnswersTeacher.study_subject)
    dp.message.register(select_task_name, GetAnswersTeacher.study_group)
    dp.message.register(show_all_answers, GetAnswersTeacher.task_name)
