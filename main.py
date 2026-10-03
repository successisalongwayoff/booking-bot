import asyncio
import logging

from aiogram import Bot,Dispatcher
from config import BOT_TOKEN
from database.models import init_db
from database.requests import add_services
from handlers.admins import admin_router
from handlers.user import router as user_router
from services.scheduler import setup_scheduler


async def main():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(name)s - %(message)s"
    )
    await init_db()

    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher()
    setup_scheduler(bot)
    dp.include_router(admin_router)
    dp.include_router(user_router)
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Бот выключен!")
