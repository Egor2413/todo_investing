import asyncio
from create_bot import bot, dp
from database import init_db
from handlers.start import router as start_router
from handlers.tasks import router as tasks_router
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from handlers.finances import router as finances_router
from handlers.investments import router as investments_router
from utils.scheduler import check_quarterly_snapshot_reminder


async def main():
    init_db()

    # Планировщик напоминаний
    scheduler = AsyncIOScheduler(timezone='Europe/Moscow')
    scheduler.add_job(
        check_quarterly_snapshot_reminder,
        'cron',
        day=1,
        month='1,4,7,10',
        hour=10,
        minute=0
    )
    scheduler.start()

    dp.include_router(start_router)
    dp.include_router(tasks_router)
    dp.include_router(finances_router)
    dp.include_router(investments_router)

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())