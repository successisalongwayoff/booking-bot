from apscheduler.schedulers.asyncio import AsyncIOScheduler
from aiogram import Bot
from database.requests import get_upcoming_appointments

async def send_reminders(bot: Bot):
    appointments = await get_upcoming_appointments()

    for app in appointments:
        app_id, user_id, service_name, date_time = app

        try:
            await bot.send_message(
                chat_id=user_id,
                text=(
                    f"⏰ <b>Напоминание о записи!</b>\n\n"
                    f"✂️ <b>Услуга:</b> {service_name}\n"
                    f"📅 <b>Время:</b> {date_time}\n\n"
                    f"Ждем вас в барбершопе! Если ваши планы изменились, пожалуйста, отмените запись в меню «📋 Мои записи»."
                ),
                parse_mode="HTML"
            )
        except Exception as e:
            print(f"Не удалось отправить напоминание пользователю {user_id}: {e}")

def setup_scheduler(bot:Bot):
    scheduler = AsyncIOScheduler()
    scheduler.add_job(send_reminders, "interval", minutes=60, args=[bot])
    scheduler.start()