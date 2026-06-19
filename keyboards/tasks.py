from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

# ============================================
# 1. ГЛАВНОЕ МЕНЮ ЗАДАЧ
# ============================================

def get_tasks_main_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура главного меню раздела Задачи"""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="Список задач", callback_data="tasks_list"),
                InlineKeyboardButton(text="Добавить задачу", callback_data="tasks_add")
            ],
            [
                InlineKeyboardButton(text="Завершить задачу", callback_data="tasks_complete"),
                InlineKeyboardButton(text="Удалить задачу", callback_data="tasks_delete")
            ],
            [
                InlineKeyboardButton(text="Статистика", callback_data="tasks_stats"),
                InlineKeyboardButton(text="В главное меню", callback_data="back_to_main")
            ]
        ]
    )


# ============================================
# 2. КЛАВИАТУРА ПОДТВЕРЖДЕНИЯ
# ============================================

def get_confirm_keyboard(action: str, task_id: int = None) -> InlineKeyboardMarkup:
    if action == "add":
        buttons = [
            InlineKeyboardButton(text="Да, добавить", callback_data="confirm_and_yes"),
            InlineKeyboardButton(text="Нет, отмена", callback_data="confirm_and_no"),
        ]
    elif action == "complete":
        buttons = [
            InlineKeyboardButton(text="Да, завершить", callback_data=f"confirm_complete_yes_{task_id}"),
            InlineKeyboardButton(text="Нет, отмена", callback_data="confirm_complete_no"),
        ]
    elif action == "delete":
        buttons = [
            InlineKeyboardButton(text="Да, удалить", callback_data=f"confirm_delete_yes_{task_id}"),
            InlineKeyboardButton(text="Нет, оставить", callback_data="confirm_delete_no"),
        ]
    else:
        buttons = []
    return InlineKeyboardMarkup(inline_keyboard=[buttons])

# ============================================
# 3. КНОПКА НАЗАД (для списка задач)
# ============================================

def get_back_button() -> InlineKeyboardMarkup:
    """Простая кнопка назад"""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Назад", callback_data="tasks_back_to_menu")],
        ]
    )

# ============================================
# КЛАВИАТУРА СТАТИСТИКИ
# ============================================

def get_stats_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="📊 Текущий месяц", callback_data="stats_current"),
                InlineKeyboardButton(text="📊 За 12 месяцев", callback_data="stats_last_12")
            ],
            [
                InlineKeyboardButton(text="🎯 Установить цель", callback_data="stats_set_goal")
            ],
            [
                InlineKeyboardButton(text="◀️ Назад", callback_data="tasks_back_to_menu")
            ]
        ]
    )

