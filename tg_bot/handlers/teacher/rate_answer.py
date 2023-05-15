from aiogram import Dispatcher
from aiogram import types
from aiogram.filters import Command, CommandObject
from aiogram.fsm.context import FSMContext

from tg_bot.keyboards.reply import create_cancel_keyboard
from tg_bot.misc.database import db_session, db_add_func
from tg_bot.misc.states import SelectRole, GetAnswersTeacher, RateAnswerTeacher
from tg_bot.models.models import (
    Task, User, Subject,
    TeacherSubject, Group, GroupSubject, Student, Answer, File, AnswerFile, Mark,
)
from aiogram import html


async def show_student_answers(message: types.Message, state: FSMContext):
    # получим словарь id: full_name студента
    data = await state.get_data()

    # проверим, совпадает ли введенное ФИО с одним из values словаря
    if message.text.lower() in data['students_full_names'].values():
        # найдем id студента с введенным ФИО
        student_id = [id for id, full_name in data['students_full_names'].items() if full_name == message.text.lower()][0]

        answers = db_session.query(Answer).filter_by(student_id=student_id).all()

        # Запишем id последнего ответа в MemoryStorage, дабы в дальнейшем его оценить
        last_answer_id = answers[-1].id
        await state.update_data(last_answer_id=last_answer_id)

        for index, answer in enumerate(answers):
            answer_files = db_session.query(File).join(AnswerFile).filter(AnswerFile.answer == answer).all()

            # если файлов > 1 отправляем группу документов, иначе 1 документ
            if len(answer_files) > 1:
                # преобразуем полученный список объектов класса File в список документов
                media_list = [types.InputMediaDocument(media=file.code) for file in answer_files]
                await message.answer_media_group(media=media_list)
                await message.answer(
                    text=f"Номер ответа: {index+1}\n"
                         f"Описание работы: {answer.description}"
                )
            elif len(answer_files) == 1:
                await message.answer_document(
                    document=answer_files[0].code,
                    caption=f"Номер ответа: {index+1}\n"
                            f"Описание работы: {answer.description}"
                )
            # если список файлов пуст
            else:
                await message.answer(
                    text=f"Номер ответа: {index+1}\n"
                         f"Описание работы: {answer.description}"
                )
        # Установим состояние и дадим инструкции пользователю
        await state.set_state(RateAnswerTeacher.rate_answer)
        await message.answer(
            text=html.underline(f"Чтобы оценить работу студента, введите отметку.\n"
                                f"Внимание! Оценивается последняя отправленная работа!!")
        )

    else:
        await message.answer(
            text="Вы ввели неверное ФИО студента.\n"
                 "Попробуйте еще раз."
        )


async def rate_student_answer(message: types.Message, state: FSMContext):
    # Проверим, попадает ли оценка в диапазон допустимых значений
    if int(message.text) in range(1,6):
        # Запишем оценку в MemoryStorage
        await state.update_data(student_mark=message.text)
        # Установим состояние и запросим ввести описание отметки
        await state.set_state(RateAnswerTeacher.description)
        await message.answer(
            text="Опишите, почему была поставлена такая оценка.\n"
        )
    else:
        await message.answer(
            text="Вы ввели неверную оценку.\n"
                 "Оценка должна находиться в диапазоне от 1 до 5.\n"
                 "Попробуйте еще раз."
        )


async def rate_description(message: types.Message, state: FSMContext):
    # Запишем description в MemoryStorage
    await state.update_data(description=message.text)
    # Получим данные из MemoryStorage
    rate_data = await state.get_data()
    # Создадим и добавим в БД новый экземпляр класса Mark
    new_mark = Mark(
        mark=rate_data['student_mark'],
        description=rate_data['description'],
        answer_id=rate_data['last_answer_id']
    )
    db_add_func(new_mark)

    # Установим пользователю состояние выбора другого студента для оценивания
    await state.set_state(RateAnswerTeacher.student_name)
    await message.answer(
        text='Ответ успешно оценен!\n'
             'Можете ввести ФИО следующего студента, чей ответ хотите оценить.\n'
             'Или ввести /cancel чтобы закончить оценивание работ.'
    )


def register_teacher_rate_answer(dp: Dispatcher):
    # state handlers
    dp.message.register(show_student_answers, RateAnswerTeacher.student_name)
    dp.message.register(rate_student_answer, RateAnswerTeacher.rate_answer)
    dp.message.register(rate_description, RateAnswerTeacher.description)
