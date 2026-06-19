from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

# ============================================
# 1. ГЛАВНОЕ МЕНЮ ФИНАНСОВ
# ============================================

def get_finances_main_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура главного меню раздела Задачи"""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
            InlineKeyboardButton(text='Баланс по типам активов', callback_data='type_balance'),
            InlineKeyboardButton(text='Общий баланс', callback_data='total_balance')
            ],
            [
            InlineKeyboardButton(text='Добавить счет', callback_data='add_account'),
            InlineKeyboardButton(text='Пополнить/снять', callback_data='deposit_withdraw')
            ],
            [
            InlineKeyboardButton(text='Создать цель', callback_data='add_goal'),
            InlineKeyboardButton(text="Цели", callback_data="goals_main_menu")
            ],
            [
            InlineKeyboardButton(text='История транзакций', callback_data='transaction_history')
            ]
        ]
    )

# ============================================
# 2. ПОДМЕНЮ "БАЛАНС ПО ТИПАМ"
# ============================================

def get_balance_types_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура выбора типа актива для просмотра баланса"""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
            InlineKeyboardButton(text='🏦 Вклады', callback_data='balance_savings'),
            InlineKeyboardButton(text='💵 Кэш', callback_data='balance_cash')
            ],
            [
            InlineKeyboardButton(text='@ Крипта', callback_data='balance_crypto'),
            InlineKeyboardButton(text='📈 Инвестиции', callback_data='balance_investments')
            ],
            [
            InlineKeyboardButton(text='◀️ Назад', callback_data='finances_back_to_menu')
            ]
        ]
    )

# ============================================
# 3. ПОДМЕНЮ "ПОПОЛНИТЬ/СНЯТЬ"
# ============================================

def get_deposit_withdraw_keyboard(account_id: int) -> InlineKeyboardMarkup:
    """Клавиатура выбора действия для конкретного счёта"""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
            InlineKeyboardButton(text='💰 Пополнить', callback_data=f'deposit_{account_id}'),
            InlineKeyboardButton(text='💸 Снять', callback_data=f'withdraw_{account_id}')
            ],
            [
            InlineKeyboardButton(text='◀️ Назад', callback_data='finances_back_to_menu')
            ]
        ]
    )


# ============================================
# 5. ПОДМЕНЮ "ИСТОРИЯ ТРАНЗАКЦИЙ"
# ============================================

def get_account_selection_keyboard(account_id: int) -> InlineKeyboardMarkup:
    """Клавиатура для просмотра истории транзакций по счетам"""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
            InlineKeyboardButton(text='📜 Показать историю', callback_data=f'show_history_{account_id}'),
            InlineKeyboardButton(text='◀️ Назад', callback_data='finances_back_to_menu')
            ],
        ]
    )

# ============================================
# 6. КНОПКА "НАЗАД" (общая)
# ============================================

def get_finances_back_button() -> InlineKeyboardMarkup:
    """Простая кнопка назад в главное меню финансов"""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text='◀️ Назад', callback_data='finances_back_to_menu')
            ]
        ]
    )

# ============================================
# 7. ВЫБОР ТИПА СЧЁТА (для добавления)
# ============================================

def get_account_types_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура выбора типа счёта при добавлении"""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="🏦 Вклады", callback_data="account_type_savings"),
                InlineKeyboardButton(text="💵 Кэш", callback_data="account_type_cash")
            ],
            [
                InlineKeyboardButton(text="🪙 Крипта", callback_data="account_type_crypto"),
                InlineKeyboardButton(text="📈 Инвестиции", callback_data="account_type_investments")
            ],
            [
                InlineKeyboardButton(text="◀️ Назад", callback_data="finances_back_to_menu")
            ]
        ]
    )


def get_goal_actions_keyboard(goal_id: int) -> InlineKeyboardMarkup:
    """Клавиатура действий с выбранной целью"""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="💰 Пополнить", callback_data=f"goal_deposit_{goal_id}"),
                InlineKeyboardButton(text="✅ Завершить", callback_data=f"goal_complete_{goal_id}")
            ],
            [
                InlineKeyboardButton(text="🗑️ Удалить", callback_data=f"goal_delete_{goal_id}")
            ],
            [
                InlineKeyboardButton(text="◀️ Назад", callback_data="finances_back_to_menu")
            ]
        ]
    )


def get_goal_selection_keyboard(goals: list) -> InlineKeyboardMarkup:
    """Клавиатура выбора цели из списка"""
    rows = []
    for goal in goals:
        # Проверка: если target_amount = 0, прогресс = 0
        if goal.target_amount and goal.target_amount > 0:
            progress = (goal.current_amount / goal.target_amount) * 100
        else:
            progress = 0

        rows.append([
            InlineKeyboardButton(
                text=f"🎯 {goal.name} ({progress:.0f}%)",
                callback_data=f"select_goal_{goal.id}"
            )
        ])

    rows.append([
        InlineKeyboardButton(text="◀️ Назад", callback_data="finances_back_to_menu")
    ])

    return InlineKeyboardMarkup(inline_keyboard=rows)


def get_goals_main_keyboard() -> InlineKeyboardMarkup:
    """Главное меню целей"""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="📋 Активные", callback_data="goals_active"),
                InlineKeyboardButton(text="✅ Выполненные", callback_data="goals_achieved")
            ],
            [
                InlineKeyboardButton(text="➕ Новая цель", callback_data="add_goal")
            ],
            [
                InlineKeyboardButton(text="◀️ Назад", callback_data="finances_back_to_menu")
            ]
        ]
    )















