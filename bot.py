import asyncio

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from tg_bot.config import load_config
from tg_bot.handlers.general import register_general
from tg_bot.handlers.student.get_task import register_student_select_task
from tg_bot.handlers.student.register import register_student
from tg_bot.handlers.student.send_answer import register_student_send_answer
from tg_bot.handlers.teacher.add_task import register_teacher_add_task
from tg_bot.handlers.teacher.register import register_teacher
from tg_bot.handlers.teacher.get_answers import register_teacher_get_answers
from tg_bot.misc.database import db_init


def register_all_handlers(dp: Dispatcher):
    register_general(dp)
    register_teacher(dp)
    register_teacher_add_task(dp)
    register_teacher_get_answers(dp)
    register_student(dp)
    register_student_select_task(dp)
    register_student_send_answer(dp)


async def main():
    # load config from .env file
    config = load_config(".env")
    # initialize MemoryStorage for FSM
    storage = MemoryStorage()
    # create instances of Bot and Dispatcher objects
    bot = Bot(token=config.tg_bot.token, parse_mode='HTML')
    dp = Dispatcher(bot=bot, storage=storage)
    # register all handlers
    register_all_handlers(dp)
    # initialize the database
    db_init()
    # start
    try:
        await bot.delete_webhook(drop_pending_updates=True)
        await dp.start_polling(bot)
    finally:
        await dp.storage.close()
        await bot.session.close()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        print('Bot stopped!!!')
