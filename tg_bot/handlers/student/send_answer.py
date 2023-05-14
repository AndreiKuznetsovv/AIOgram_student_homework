from aiogram import Dispatcher
from aiogram import types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from tg_bot.keyboards.reply import create_cancel_keyboard
from tg_bot.misc.database import db_session, db_add_func
from tg_bot.misc.states import SendAnswerStudent, SelectRole
from tg_bot.models.models import (
    Answer, File, Teacher,
    User, GroupSubject, Subject,
    TeacherSubject, AnswerFile, Task,
)


async def select_subject(message: types.Message, state: FSMContext):
    # установим состояние и запросим название предмета
    await state.set_state(SendAnswerStudent.study_subject)
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
        await state.set_state(SendAnswerStudent.teacher_full_name)
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

        # Проверим, добавил ли преподаватель задания по выбранному предмету
        teacher = db_session.query(Teacher).join(User).join(TeacherSubject).filter(
            User.full_name == message.text.lower(),
            TeacherSubject.subject_id == data['subject_id']
        ).first()
        if teacher:
            # Добавим в MemoryStorage id преподавателя
            await state.update_data(teacher_id=teacher.id)

            # установим состояние и запросим название задания
            await state.set_state(SendAnswerStudent.task_name)
            await message.answer(
                text="Введите название задания.",
                reply_markup=create_cancel_keyboard()  # Добавить клавиатуру для выбора группы
            )
        else:
            await message.answer(
                text="Преподавателя с таким ФИО не существует\n"
                     "или он не добавил заданий по выбранному предмету."
                     "Попробуйте ввести ФИО преподавателя еще раз."
            )
    else:
        # ФИО состоит не из трёх слов
        await message.answer(
            text="ФИО должно состоять из 3-ёх слов"
        )


async def request_description(message: types.Message, state: FSMContext):
    task_exists = db_session.query(Task).filter_by(name=message.text.lower()).first()
    if task_exists:
        # Запишем id предмета в MemoryStorage
        await state.update_data(task_id=task_exists.id)

        # Установим состояние и запросим описание ответа на задание
        await state.set_state(SendAnswerStudent.description)
        await message.answer(
            text="Введите описание вашего ответа/решения, которое вы собираетесь отправить преподавателю."
        )
    else:
        await message.answer(
            text="Задания с таким названием не существует.\n"
                 "Попробуйте ввести название задания еще раз."
        )


async def send_answer(message: types.Message, state: FSMContext):
    # Запишем описание задания в MemoryStorage
    await state.update_data(description=message.text)

    # Получим все данные из MemoryStorage
    answer_data = await state.get_data()

    # Создадим новый объект класса Answer и сохраним его в БД
    new_answer = Answer(
        task_id=answer_data['task_id'],
        description=answer_data['description'],
        student_id=answer_data['student_id']
    )
    db_add_func(new_answer)

    # Очистим MemoryStorage
    await state.set_data({})

    # загрузим task_id в MemoryStorage, чтобы указать к какому заданию прикрепляются файлы
    await state.update_data(task_id=new_answer.id)

    # Установим состояние и запросим добавление файлов
    await state.set_state(SendAnswerStudent.upload_file)
    await message.answer(
        text='Ответ на задание успешно добавлен!\n'
             'Теперь добавьте файлы к вашему ответу.'
    )

    # вывод данных на экран для теста
    serialized_answer = ""
    for key, value in answer_data.items():
        serialized_answer += f"{key}: {value}\n"
    await message.answer(
        text=f"{serialized_answer}"
    )


async def upload_files(message: types.Message, state: FSMContext):
    # Получим все данные из MemoryStorage
    answer_data = await state.get_data()

    # Добавим файл в БД (с проверкой на расширение файла)
    try:
        new_file = File(code=message.document.file_id)
        db_add_func(new_file)
        new_answer_file = AnswerFile(file_id=new_file.id, answer_id=answer_data['task_id'])
        db_add_func(new_answer_file)
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
        reply_markup=None  # reply клавиатура с командой cancel
    )


def register_student_send_answer(dp: Dispatcher):
    # Command handlers
    dp.message.register(select_subject, Command('send_answer', ignore_case=True), SelectRole.student)
    # state handlers
    dp.message.register(select_teacher, SendAnswerStudent.study_subject)
    dp.message.register(select_task_name, SendAnswerStudent.teacher_full_name)
    dp.message.register(request_description, SendAnswerStudent.task_name)
    dp.message.register(send_answer, SendAnswerStudent.description)
    dp.message.register(upload_files, SendAnswerStudent.upload_file)
