from aiogram import Dispatcher
from aiogram import types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from tg_bot.misc.states import TaskInteractionTeacher

from tg_bot.models.models import Task, File
from tg_bot.misc.database import db_add_func, db_session

async def request_study_group(message: types.Message, state: FSMContext):
    await message.answer(
        text="Введите название группы, с заданиями которой хотите взаимодействовать.",
        reply_markup=None
    )
    await state.set_state(TaskInteractionTeacher.study_group)


async def check_study_group(message: types.Message, state: FSMContext):
    if len(message.text.split('-')) == 2:
        await state.update_data(study_group=message.text)
        await message.answer(
            text="Введите название предмета.",
            reply_markup=None
        )
        await state.set_state(TaskInteractionTeacher.study_subject)
    else:
        await message.answer(
            text="Вы ввели неверное название группы.\n"
                 "Оно должно состоять из 2-ух словах, разделенных тире.\n"
                 "Попробуйте еще раз."
        )

async def check_study_subject(message: types.Message, state: FSMContext):
    await state.update_data(study_subject=message.text)
    await message.answer(
        text="Введите название задания."
    )
    await state.set_state(TaskInteractionTeacher.task_name)


async def check_task_name(message: types.Message, state: FSMContext):
    await state.update_data(task_name=message.text)
    await message.answer(
        text="Введите описание задания."
    )
    await state.set_state(TaskInteractionTeacher.description)


async def upload_task(message: types.Message, state: FSMContext):
    await state.update_data(description=message.text)
    task_data = await state.get_data()
    new_task = Task(group=task_data['study_group'], subject=task_data['study_subject'],
                    task_name=task_data['task_name'], description=task_data['description'],
                    teacher_id=task_data['teacher_id'])
    db_add_func(new_task)
    # загрузим task_id в MemoryStorage, чтобы указать к какому заданию прикрепляются файлы
    await state.update_data(task_id=new_task.id)
    await message.answer(
        text='Задание успешно добавлено!\n'
             'Теперь добавьте файлы к заданию.'
    )
    await state.set_state(TaskInteractionTeacher.upload_file)
    # вывод данных на экран для теста
    serialized_answer = ""
    for key, value in task_data.items():
        serialized_answer += f"{key}: {value}\n"
    await message.answer(
        text=f"{serialized_answer}"
    )


async def upload_files(message: types.Message, state: FSMContext):
    task_data = await state.get_data()
    try:
        new_file = File(code=message.document.file_id, task_id=task_data['task_id'])
        db_add_func(new_file)
    except AttributeError:
        await message.answer(
            text="Файл с данным расширением добавить невозможно.\n"
                 "Если вы хотите загрузить изображение, уберите галочку с \"Сжать изображение\""
        )
        return
    db_add_func(new_file)
    await message.answer(
        text='Файл успешно добавлен!\n'
             'Вы можете продолжить добавление файлов!\n'
             'Или ввести команду /cancel чтобы закончить добавление файлов.',
        reply_markup=None # reply клавиатура с командой cancel
    )


async def command_cancel(message: types.Message, state: FSMContext):
    """
    Позволяет пользователю отменить любое действие
    """
    current_state = await state.get_state()
    if current_state is None:
        return

    await state.clear()
    await message.reply('Отмена произошла успешно!')


def register_task_teacher(dp: Dispatcher):
    # cancel handler
    dp.message.register(command_cancel, Command('cancel'))
    # state handlers
    dp.message.register(request_study_group, Command('tasks'), TaskInteractionTeacher.teacher) # Добавить проверку на ContentType
    dp.message.register(check_study_group, TaskInteractionTeacher.study_group)
    dp.message.register(check_study_subject, TaskInteractionTeacher.study_subject)
    dp.message.register(check_task_name, TaskInteractionTeacher.task_name)
    dp.message.register(upload_task, TaskInteractionTeacher.description)
    dp.message.register(upload_files, TaskInteractionTeacher.upload_file)
