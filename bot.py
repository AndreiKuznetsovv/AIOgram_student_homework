import asyncio

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from tg_bot.config import load_config
from tg_bot.handlers.general import register_general
from tg_bot.handlers.student.select_tasks import register_student
from tg_bot.handlers.teacher.register import register_teacher
from tg_bot.handlers.teacher.add_tasks import register_task_teacher

from tg_bot.misc.database import db_init

def register_all_handlers(dp: Dispatcher):
    register_general(dp)
    register_teacher(dp)
    register_student(dp)
    register_task_teacher(dp)


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
