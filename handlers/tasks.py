from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from datetime import datetime
from keyboards.tasks import get_tasks_main_keyboard, get_confirm_keyboard, get_back_button, get_stats_keyboard
from states.tasks import AddTaskStates
from database.db import (
    add_task,
    get_active_tasks,
    get_completed_tasks,
    get_completed_tasks_by_month,
    complete_task,
    delete_task,
    update_monthly_stats,
    get_monthly_stats,
    session,
    MonthlyStats,
    get_last_n_months_stats,
    get_average_monthly_points,
)

router = Router()

# ============================================
# 1. КОМАНДА /tasks — показать меню задач
# ============================================

@router.message(Command("tasks"))
async def cmd_tasks(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(
        "<b>Управление задачами</b>\n\n"
        "Выбери действие:",
        reply_markup=get_tasks_main_keyboard()
    )

# ============================================
# 2. ВОЗВРАТ В ГЛАВНОЕ МЕНЮ ЗАДАЧ
# ============================================

@router.callback_query(F.data == "tasks_back_to_menu")
async def back_to_tasks_menu(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.answer()
    await callback.message.edit_reply_markup(reply_markup=None)
    await callback.message.answer(
        "<b>Управление задачами</b>\n\nВыбери действие:",
        reply_markup=get_tasks_main_keyboard()
    )

# ============================================
# 3. ДОБАВЛЕНИЕ ЗАДАЧИ (FSM)
# ============================================

@router.callback_query(F.data == "tasks_add")
async def start_add_task(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await callback.message.edit_reply_markup(reply_markup=None)
    await callback.message.answer("Введите название задачи")
    await state.set_state(AddTaskStates.waiting_title)

@router.message(AddTaskStates.waiting_title)
async def get_task_title(message: Message, state: FSMContext):
    await state.update_data(title=message.text)
    await message.answer("Введите дату дедлайна (в формате ГГГГ-ММ-ДД):")
    await state.set_state(AddTaskStates.waiting_due_date)

@router.message(AddTaskStates.waiting_due_date)
async def get_task_due_date(message: Message, state: FSMContext):
    await state.update_data(due_date=message.text)
    await message.answer("Сколько баллов даёт задача? (от 1 до 10):")
    await state.set_state(AddTaskStates.waiting_value)

@router.message(AddTaskStates.waiting_value)
async def get_task_value(message: Message, state: FSMContext):
    try:
        value = int(message.text)
        if value < 1 or value > 10:
            await message.answer("❌ Баллы должны быть от 1 до 10. Попробуй ещё раз:")
            return
    except ValueError:
        await message.answer("❌ Введи число от 1 до 10:")
        return

    await state.update_data(value=value)
    data = await state.get_data()

    confirm_text = (
        f"<b>Новая задача</b>\n\n"
        f"Название: {data['title']}\n"
        f"Дедлайн: {data['due_date']}\n"
        f"Баллы: {data['value']}\n\n"
        f"Добавить?"
    )

    await message.answer(
        confirm_text,
        reply_markup=get_confirm_keyboard("add")
    )
    await state.set_state(AddTaskStates.waiting_confirm)

@router.callback_query(AddTaskStates.waiting_confirm, F.data == "confirm_and_yes")
async def confirm_add_task(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    data = await state.get_data()

    task_id = add_task(
        task_title=data['title'],
        due_date=data['due_date'],
        value=data['value']
    )

    await callback.message.edit_reply_markup(reply_markup=None)
    await callback.message.answer(
        f"✅ Задача <b>«{data['title']}»</b> добавлена!\n"
        f"Баллов: {data['value']} | Дедлайн: {data['due_date']}"
    )
    await state.clear()


@router.callback_query(AddTaskStates.waiting_confirm, F.data == "confirm_and_no")
async def cancel_add_task(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await callback.message.edit_reply_markup(reply_markup=None)
    await callback.message.answer("❌ Добавление задачи отменено.")
    await state.clear()
    await cmd_tasks(callback.message, state)


# ============================================
# 4. Функции задач
# ============================================

@router.callback_query(F.data == "tasks_list")
async def tasks_list(callback: CallbackQuery):
    await callback.answer()
    await callback.message.edit_reply_markup(reply_markup=None)

    tasks = get_active_tasks()

    if not tasks:
        text = "У тебя нет активных задач"
    else:
        text = "<b>Твои задачи:</b>\n\n"
        for task in tasks:
            text += f"• {task.task} | до {task.due_date.strftime('%d.%m.%Y')} | {task.value} баллов\n"

    await callback.message.answer(text, reply_markup=get_back_button())


@router.callback_query(F.data == "tasks_complete")
async def tasks_complete(callback: CallbackQuery):
    await callback.answer()

    tasks = get_active_tasks()

    if not tasks:
        await callback.message.answer("Нет активных задач для выполнения")
        return

    rows = []
    for task in tasks:
        rows.append([
            InlineKeyboardButton(
                text=f"{task.task} ({task.value} баллов)",
                callback_data=f"complete_task_{task.id}"
            )
        ])
    rows.append([
        InlineKeyboardButton(text="◀Назад", callback_data="tasks_back_to_menu")
    ])

    keyboard = InlineKeyboardMarkup(inline_keyboard=rows)

    await callback.message.answer(
        "Выбери задачу для выполнения:",
        reply_markup=keyboard
    )


@router.callback_query(F.data.startswith("complete_task_"))
async def execute_complete(callback: CallbackQuery):
    await callback.answer()
    task_id = int(callback.data.split("_")[2])

    points = complete_task(task_id)
    update_monthly_stats(points)

    await callback.message.edit_reply_markup(reply_markup=None)
    await callback.message.answer(f"Задача выполнена! +{points} баллов")

    # Показываем обновлённый список задач
    await tasks_list(callback)


# ============================================
# 6. УДАЛЕНИЕ ЗАДАЧИ
# ============================================
@router.callback_query(F.data == "tasks_delete")
async def tasks_delete(callback: CallbackQuery):
    await callback.answer()

    tasks = get_active_tasks()

    if not tasks:
        await callback.message.answer("Нет активных задач для удаления")
        return

    rows = []
    for task in tasks:
        rows.append([
            InlineKeyboardButton(
                text=f"{task.task} ({task.value} баллов)",
                callback_data=f"delete_task_{task.id}"
            )
        ])
    rows.append([
        InlineKeyboardButton(text="Назад", callback_data="tasks_back_to_menu")
    ])

    keyboard = InlineKeyboardMarkup(inline_keyboard=rows)

    await callback.message.answer(
        "Выбери задачу для удаления:",
        reply_markup=keyboard
    )


@router.callback_query(F.data.startswith("delete_task_"))
async def execute_delete(callback: CallbackQuery):
    await callback.answer()
    task_id = int(callback.data.split("_")[2])

    delete_task(task_id)

    await callback.message.edit_reply_markup(reply_markup=None)
    await callback.message.answer("Задача удалена!")

    # Показываем обновлённый список задач
    await tasks_list(callback)

# ============================================
# 7. Статистика баллов по задачам
# ============================================
@router.callback_query(F.data == "tasks_stats")
async def tasks_stats_menu(callback: CallbackQuery):
    """Показать подменю статистики"""
    await callback.answer()
    await callback.message.edit_reply_markup(reply_markup=None)
    await callback.message.answer(
        "📊 <b>Меню статистики</b>\n\n"
        "Выбери действие:",
        reply_markup=get_stats_keyboard()
    )


@router.callback_query(F.data == "stats_current")
async def stats_current_month(callback: CallbackQuery):
    """Показать статистику за текущий месяц"""
    await callback.answer()
    await callback.message.edit_reply_markup(reply_markup=None)

    now = datetime.now()
    year = now.year
    month = now.month

    stats = get_monthly_stats(year, month)

    if stats:
        text = f"📊 <b>Статистика за {month}.{year}</b>\n\n"
        text += f"🏆 Набрано баллов: {stats.points}\n"
        text += f"🎯 Цель: {stats.target_points}\n"
        if stats.target_points > 0:
            progress = (stats.points / stats.target_points) * 100
            text += f"📈 Прогресс: {progress:.1f}%"
    else:
        text = "📊 В этом месяце пока нет баллов"

    await callback.message.answer(text, reply_markup=get_stats_keyboard())

@router.callback_query(F.data == "stats_set_goal")
async def stats_set_goal(callback: CallbackQuery, state: FSMContext):
    """Начать установку цели на месяц"""
    await callback.answer()
    await callback.message.edit_reply_markup(reply_markup=None)
    await callback.message.answer(
        "🎯 Введите количество баллов, которое хочешь набрать за этот месяц.\n\n"
        "Например: 500"
    )
    await state.set_state(AddTaskStates.waiting_goal)


@router.message(AddTaskStates.waiting_goal)
async def process_goal_input(message: Message, state: FSMContext):
    try:
        goal = int(message.text)
        if goal < 0:
            await message.answer("❌ Цель должна быть положительной. Введите число > 0:")
            return
    except ValueError:
        await message.answer("❌ Введите число (например: 500):")
        return

    now = datetime.now()
    stats = get_monthly_stats(now.year, now.month)

    # Получаем сессию
    db_session = session()

    if stats:
        stats.target_points = goal
    else:
        stats = MonthlyStats(
            year=now.year,
            month=now.month,
            points=0,
            target_points=goal
        )
        db_session.add(stats)

    db_session.commit()
    db_session.close()

    await state.clear()
    await message.answer(
        f"✅ Цель на месяц установлена: {goal} баллов!\n\n"
        f"Теперь можно вернуться в меню статистики.",
        reply_markup=get_stats_keyboard()
    )


@router.callback_query(F.data == "stats_last_12")
async def stats_last_12_months(callback: CallbackQuery):
    """Показать статистику за последние 12 месяцев и средний показатель"""
    await callback.answer()
    await callback.message.edit_reply_markup(reply_markup=None)

    stats_list = get_last_n_months_stats(12)
    avg_points = get_average_monthly_points()

    text = "📊 <b>Статистика</b>\n\n"

    # Последние 12 месяцев
    if stats_list:
        text += "📅 <b>Последние 12 месяцев:</b>\n"
        for stat in reversed(stats_list):
            month_name = f"{stat.month:02d}.{stat.year}"
            bar = "█" * min(int(stat.points / 10), 10) if stat.points > 0 else "░"
            text += f"  {month_name}: {stat.points} баллов {bar}\n"
    else:
        text += "📅 За последние 12 месяцев данных нет.\n"

    # Средний показатель
    text += f"\n📊 <b>Средний балл в месяц:</b> {avg_points:.1f}"

    await callback.message.answer(text, reply_markup=get_stats_keyboard())


@router.callback_query(F.data == "tasks_completed")
async def tasks_completed_menu(callback: CallbackQuery, state: FSMContext):
    """Меню выбора месяца для просмотра выполненных задач"""
    await callback.answer()
    await callback.message.edit_reply_markup(reply_markup=None)

    await callback.message.answer(
        "✅ <b>Выполненные задачи</b>\n\n"
        "Введите месяц в формате <b>ГГГГ-ММ</b>\n"
        "Например: 2025-06",
        reply_markup=get_back_button()
    )
    await state.set_state(AddTaskStates.waiting_completed_month)


@router.message(AddTaskStates.waiting_completed_month)
async def show_completed_tasks_by_month(message: Message, state: FSMContext):
    """Показать выполненные задачи за указанный месяц"""
    try:
        year, month = map(int, message.text.split('-'))
        if month < 1 or month > 12:
            raise ValueError
    except ValueError:
        await message.answer(
            "❌ Неверный формат. Введите месяц в формате <b>ГГГГ-ММ</b>\n"
            "Например: 2025-06"
        )
        return

    tasks = get_completed_tasks_by_month(year, month)

    if not tasks:
        await message.answer(
            f"📋 За {month:02d}.{year} нет выполненных задач",
            reply_markup=get_back_button()
        )
    else:
        text = f"✅ <b>Выполненные задачи за {month:02d}.{year}</b>\n\n"
        total_points = 0
        for task in tasks:
            done_date = task.done_date.strftime('%d.%m.%Y') if task.done_date else "—"
            text += f"• {task.task} | +{task.value} баллов | {done_date}\n"
            total_points += task.value
        text += f"\n💰 <b>Всего баллов за месяц:</b> {total_points}"

        await message.answer(text, reply_markup=get_back_button())

    await state.clear()
