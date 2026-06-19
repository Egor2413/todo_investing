from datetime import datetime
from create_bot import bot
from database.db import is_snapshot_window_open, get_next_quarter_start


async def check_quarterly_snapshot_reminder():
    """Отправляет напоминание админу в первый день окна снимка"""
    now = datetime.now()

    # Проверяем, что сегодня 1-е число и месяц — первый в квартале
    if now.day != 1 or now.month not in [1, 4, 7, 10]:
        return

    quarter = (now.month - 1) // 3 + 1

    text = (
        f"🔔 <b>Окно для создания квартального снимка открыто!</b>\n\n"
        f"📅 Сегодня 1-е число {quarter}-го квартала.\n"
        f"📸 Окно открыто до <b>10 числа</b>.\n\n"
        f"Не забудь создать снимок портфеля в разделе «Инвестиции»."
    )

    # Отправляем админу (твой Telegram ID)
    from config import ADMIN_ID
    try:
        await bot.send_message(ADMIN_ID, text)
    except Exception as e:
        print(f"Ошибка отправки напоминания: {e}")