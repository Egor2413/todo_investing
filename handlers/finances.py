from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from datetime import datetime

from keyboards.finances import (
    get_finances_main_keyboard,
    get_balance_types_keyboard,
    get_deposit_withdraw_keyboard,
    get_account_selection_keyboard,
    get_finances_back_button,
    get_account_types_keyboard,
    get_goal_actions_keyboard,      # ← добавить в keyboards.finances
    get_goal_selection_keyboard,    # ← добавить в keyboards.finances
    get_goals_main_keyboard         # ← добавить в keyboards.finances
)
from states.finances import (
    AddAccountStates,
    DepositWithdrawStates,
    AddGoalStates,
    SelectStates,
    GoalActionStates
)
from database.db import (
    get_balance_by_currency,
    get_balance_by_type,
    add_account,
    update_balance,
    get_accounts_by_type,
    get_account_by_id,
    add_goal,
    get_goal_by_id,
    get_transactions_by_account,
    add_money_to_goal,
    complete_goal_manually,
    delete_goal,
    get_active_goals,
    get_achieved_goals
)

router = Router()


# ============================================
# 1. КОМАНДА /finances
# ============================================

@router.message(Command("finances"))
async def cmd_finances(message: Message, state: FSMContext):
    """Показать главное меню финансов"""
    await state.clear()
    await message.answer(
        "💰 <b>Управление финансами</b>\n\n"
        "Выбери действие:",
        reply_markup=get_finances_main_keyboard(),
    )


# ============================================
# 2. ВОЗВРАТ В ГЛАВНОЕ МЕНЮ
# ============================================

@router.callback_query(F.data == "finances_back_to_menu")
async def back_to_finance_menu(callback: CallbackQuery, state: FSMContext):
    """Вернуться в главное меню финансов"""
    await state.clear()
    await callback.answer()
    await callback.message.edit_reply_markup(reply_markup=None)
    await callback.message.answer(
        "💰 <b>Управление финансами</b>\n\nВыбери действие:",
        reply_markup=get_finances_main_keyboard()
    )


# ============================================
# 3. ОБЩИЙ БАЛАНС
# ============================================

@router.callback_query(F.data == "total_balance")
async def show_total_balance(callback: CallbackQuery):
    await callback.answer()
    await callback.message.edit_reply_markup(reply_markup=None)

    balances = get_balance_by_currency()

    if not balances:
        await callback.message.answer(
            "💰 Баланс пуст. Добавьте счёт через 'Добавить счёт'.",
            reply_markup=get_finances_back_button()
        )
        return

    text = "💰 <b>Общий баланс</b>\n\n"
    for currency, amount in balances.items():
        text += f"💵 <b>{currency}</b>: {amount:,.0f}\n"

    await callback.message.answer(text, reply_markup=get_finances_back_button())


# ============================================
# 4. БАЛАНС ПО ТИПАМ
# ============================================

@router.callback_query(F.data == "type_balance")
async def balance_by_type_start(callback: CallbackQuery, state: FSMContext):
    """Начать выбор типа для просмотра баланса"""
    await callback.answer()
    await callback.message.edit_reply_markup(reply_markup=None)
    await callback.message.answer(
        "Выберите тип актива:",
        reply_markup=get_balance_types_keyboard(),
    )
    await state.set_state(SelectStates.selecting_type)


@router.callback_query(SelectStates.selecting_type, F.data.startswith("balance_"))
async def show_balance_by_type(callback: CallbackQuery, state: FSMContext):
    """Показать баланс по выбранному типу"""
    await callback.answer()

    type_map = {
        "balance_savings": "savings",
        "balance_cash": "cash",
        "balance_crypto": "crypto",
        "balance_investments": "investments"
    }
    account_type = type_map.get(callback.data)
    balance = get_balance_by_type(account_type)

    type_name = {
        "savings": "🏦 Вклады",
        "cash": "💵 Кэш",
        "crypto": "🪙 Крипта",
        "investments": "📈 Инвестиции"
    }

    await callback.message.edit_reply_markup(reply_markup=None)
    await callback.message.answer(
        f"{type_name.get(account_type, 'Актив')}: {balance} ₽",
        reply_markup=get_finances_back_button()
    )
    await state.clear()


# ============================================
# 5. ДОБАВЛЕНИЕ СЧЁТА
# ============================================

@router.callback_query(F.data == "add_account")
async def start_add_account(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await callback.message.edit_reply_markup(reply_markup=None)
    await callback.message.answer(
        "Выберите тип счёта:",
        reply_markup=get_account_types_keyboard()
    )
    await state.set_state(AddAccountStates.waiting_type)


@router.callback_query(AddAccountStates.waiting_type, F.data.startswith("account_type_"))
async def process_account_type(callback: CallbackQuery, state: FSMContext):
    await callback.answer()

    type_map = {
        "account_type_savings": "savings",
        "account_type_cash": "cash",
        "account_type_crypto": "crypto",
        "account_type_investments": "investments"
    }
    account_type = type_map.get(callback.data, "cash")
    await state.update_data(account_type=account_type)

    await callback.message.edit_reply_markup(reply_markup=None)
    await callback.message.answer("Введите название счёта (например, 'Т-Банк', 'USDT'):")
    await state.set_state(AddAccountStates.waiting_name)


@router.message(AddAccountStates.waiting_name)
async def process_account_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await message.answer("Введите валюту (RUB, USD, EUR):")
    await state.set_state(AddAccountStates.waiting_currency)


@router.message(AddAccountStates.waiting_currency)
async def process_account_currency(message: Message, state: FSMContext):
    currency = message.text.upper()
    if currency not in ["RUB", "USD", "EUR"]:
        await message.answer("❌ Введите одну из валют: RUB, USD, EUR")
        return
    await state.update_data(currency=currency)
    await message.answer("Введите начальный баланс (число):")
    await state.set_state(AddAccountStates.waiting_balance)


@router.message(AddAccountStates.waiting_balance)
async def process_account_balance(message: Message, state: FSMContext):
    try:
        balance = int(message.text)
        if balance < 0:
            await message.answer("❌ Баланс не может быть отрицательным. Введите число >= 0:")
            return
    except ValueError:
        await message.answer("❌ Введите число:")
        return

    data = await state.get_data()
    account_id = add_account(
        account_type=data['account_type'],
        name=data['name'],
        currency=data['currency'],
        balance=balance
    )

    await message.answer(
        f"✅ Счёт <b>«{data['name']}»</b> добавлен!\n"
        f"Тип: {data['account_type']}\n"
        f"Валюта: {data['currency']}\n"
        f"Баланс: {balance} {data['currency']}"
    )
    await state.clear()


# ============================================
# 6. ПОПОЛНИТЬ/СНЯТЬ
# ============================================

@router.callback_query(F.data == "deposit_withdraw")
async def start_deposit_withdraw(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await callback.message.edit_reply_markup(reply_markup=None)

    accounts = get_accounts_by_type()

    if not accounts:
        await callback.message.answer(
            "❌ У вас нет ни одного счёта. Сначала добавьте счёт через 'Добавить счёт'.",
            reply_markup=get_finances_back_button()
        )
        return

    rows = []
    for acc in accounts:
        rows.append([
            InlineKeyboardButton(
                text=f"{acc.name} ({acc.balance} {acc.currency})",
                callback_data=f"select_account_{acc.id}"
            )
        ])
    rows.append([
        InlineKeyboardButton(text="◀️ Назад", callback_data="finances_back_to_menu")
    ])

    keyboard = InlineKeyboardMarkup(inline_keyboard=rows)

    await callback.message.answer(
        "Выберите счёт:",
        reply_markup=keyboard
    )
    await state.set_state(DepositWithdrawStates.waiting_account)


@router.callback_query(DepositWithdrawStates.waiting_account, F.data.startswith("select_account_"))
async def select_account(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    account_id = int(callback.data.split("_")[2])
    await state.update_data(account_id=account_id)

    await callback.message.edit_reply_markup(reply_markup=None)
    await callback.message.answer(
        "Выберите действие:",
        reply_markup=get_deposit_withdraw_keyboard(account_id)
    )
    await state.set_state(DepositWithdrawStates.waiting_action)


@router.callback_query(DepositWithdrawStates.waiting_action, F.data.startswith("deposit_"))
async def process_deposit(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    account_id = int(callback.data.split("_")[1])
    await state.update_data(account_id=account_id, action="deposit")

    await callback.message.edit_reply_markup(reply_markup=None)
    await callback.message.answer("Введите сумму для пополнения:")
    await state.set_state(DepositWithdrawStates.waiting_amount)


@router.callback_query(DepositWithdrawStates.waiting_action, F.data.startswith("withdraw_"))
async def process_withdraw(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    account_id = int(callback.data.split("_")[1])
    await state.update_data(account_id=account_id, action="withdraw")

    await callback.message.edit_reply_markup(reply_markup=None)
    await callback.message.answer("Введите сумму для снятия:")
    await state.set_state(DepositWithdrawStates.waiting_amount)


@router.message(DepositWithdrawStates.waiting_amount)
async def process_amount(message: Message, state: FSMContext):
    try:
        amount = int(message.text)
        if amount <= 0:
            await message.answer("❌ Сумма должна быть больше 0. Введите число:")
            return
    except ValueError:
        await message.answer("❌ Введите число:")
        return

    data = await state.get_data()
    account_id = data['account_id']
    action = data['action']

    if action == "withdraw":
        amount = -amount

    new_balance = update_balance(account_id, amount)

    if new_balance == -1:
        await message.answer("❌ Недостаточно средств на счете!")
    else:
        action_text = "пополнен" if action == "deposit" else "снятие"
        await message.answer(
            f"✅ Счёт успешно {action_text}!\n"
            f"Новый баланс: {new_balance} ₽"
        )

    await state.clear()


# ============================================
# 7. СОЗДАНИЕ ЦЕЛИ
# ============================================

@router.callback_query(F.data == "add_goal")
async def start_add_goal(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await callback.message.edit_reply_markup(reply_markup=None)
    await callback.message.answer("Введите название цели (например, 'Купить квартиру'):")
    await state.set_state(AddGoalStates.waiting_name)


@router.message(AddGoalStates.waiting_name)
async def process_goal_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await message.answer("Введите целевую сумму (в рублях):")
    await state.set_state(AddGoalStates.waiting_target)


@router.message(AddGoalStates.waiting_target)
async def process_goal_target(message: Message, state: FSMContext):
    try:
        target = int(message.text)
        if target <= 0:
            await message.answer("❌ Сумма должна быть больше 0. Введите число:")
            return
    except ValueError:
        await message.answer("❌ Введите число:")
        return

    await state.update_data(target=target)
    await message.answer(
        "Введите срок достижения цели (в формате ГГГГ-ММ-ДД)\n"
        "Или отправьте 'нет', если без срока:"
    )
    await state.set_state(AddGoalStates.waiting_deadline)


@router.message(AddGoalStates.waiting_deadline)
async def process_goal_deadline(message: Message, state: FSMContext):
    deadline = None
    if message.text.lower() != "нет":
        try:
            deadline = message.text
            datetime.strptime(deadline, "%Y-%m-%d")
        except ValueError:
            await message.answer("❌ Неверный формат. Введите дату в формате ГГГГ-ММ-ДД или 'нет':")
            return

    data = await state.get_data()
    goal_id = add_goal(
        name=data['name'],
        target_amount=data['target'],
        deadline=deadline
    )

    deadline_text = deadline if deadline else "не указан"

    await message.answer(
        f"✅ Цель <b>«{data['name']}»</b> создана!\n"
        f"Целевая сумма: {data['target']} ₽\n"
        f"Срок: {deadline_text}\n\n"
        f"📊 Теперь ты можешь пополнять цель вручную через раздел 'Цели'."
    )
    await state.clear()


# ============================================
# 8. ЦЕЛИ — ГЛАВНОЕ МЕНЮ
# ============================================

@router.callback_query(F.data == "goals_main_menu")
async def goals_main_menu(callback: CallbackQuery):
    """Главное меню целей"""
    await callback.answer()
    await callback.message.edit_reply_markup(reply_markup=None)
    await callback.message.answer(
        "🎯 <b>Управление целями</b>\n\n"
        "Здесь ты можешь создавать, пополнять и завершать свои цели.",
        reply_markup=get_goals_main_keyboard()
    )


# ============================================
# 9. ЦЕЛИ — СПИСОК
# ============================================

@router.callback_query(F.data == "goals_active")
async def goals_active_list(callback: CallbackQuery, state: FSMContext):
    """Показать список активных целей"""
    await callback.answer()
    await callback.message.edit_reply_markup(reply_markup=None)

    goals = get_active_goals()

    if not goals:
        await callback.message.answer(
            "❌ У тебя нет активных целей.\n\n"
            "Нажми «➕ Новая цель», чтобы создать первую цель!",
            reply_markup=get_goals_main_keyboard()
        )
        return

    text = "🎯 <b>Активные цели</b>\n\n"
    for goal in goals:
        progress = (goal.current_amount / goal.target_amount) * 100 if goal.target_amount and goal.target_amount > 0 else 0
        bar = "█" * int(progress / 5) + "░" * (20 - int(progress / 5))
        text += f"📌 <b>{goal.name}</b>\n"
        text += f"   {bar} {progress:.1f}%\n"
        text += f"   {goal.current_amount} / {goal.target_amount} ₽\n"
        if goal.deadline:
            text += f"   📅 Срок: {goal.deadline.strftime('%d.%m.%Y')}\n"
        text += "\n"

    text += "👇 Нажми на цель, чтобы управлять ей:"

    await callback.message.answer(
        text,
        reply_markup=get_goal_selection_keyboard(goals)
    )
    await state.set_state(GoalActionStates.waiting_goal_selection)


@router.callback_query(F.data == "goals_achieved")
async def goals_achieved_list(callback: CallbackQuery):
    """Показать список выполненных целей"""
    await callback.answer()
    await callback.message.edit_reply_markup(reply_markup=None)

    goals = get_achieved_goals()

    if not goals:
        await callback.message.answer(
            "✅ У тебя пока нет выполненных целей.\n\n"
            "Продолжай работать над своими целями!",
            reply_markup=get_goals_main_keyboard()
        )
        return

    text = "✅ <b>Выполненные цели</b>\n\n"
    for goal in goals:
        text += f"🎯 <b>{goal.name}</b>\n"
        text += f"   {goal.current_amount} / {goal.target_amount} ₽\n"
        if goal.deadline:
            text += f"   📅 Срок: {goal.deadline.strftime('%d.%m.%Y')}\n"
        text += f"   ✅ Завершена\n\n"

    await callback.message.answer(text, reply_markup=get_goals_main_keyboard())

# ============================================
# 10. ЦЕЛИ — ДЕЙСТВИЯ С ВЫБРАННОЙ ЦЕЛЬЮ
# ============================================

@router.callback_query(GoalActionStates.waiting_goal_selection, F.data.startswith("select_goal_"))
async def show_goal_actions(callback: CallbackQuery, state: FSMContext):
    """Показать детали цели и кнопки действий"""
    await callback.answer()
    goal_id = int(callback.data.split("_")[2])
    goal = get_goal_by_id(goal_id)

    if not goal:
        await callback.message.answer("❌ Цель не найдена")
        await state.clear()
        return

    progress = (goal.current_amount / goal.target_amount) * 100 if goal.target_amount else 0
    bar = "█" * int(progress / 5) + "░" * (20 - int(progress / 5))

    text = f"🎯 <b>{goal.name}</b>\n\n"
    text += f"💰 Накоплено: {goal.current_amount} ₽\n"
    text += f"🎯 Цель: {goal.target_amount} ₽\n"
    text += f"📊 Прогресс: {bar} {progress:.1f}%\n"
    if goal.deadline:
        text += f"📅 Срок: {goal.deadline.strftime('%d.%m.%Y')}\n"

    await callback.message.edit_reply_markup(reply_markup=None)
    await callback.message.answer(
        text,
        reply_markup=get_goal_actions_keyboard(goal_id)
    )
    await state.clear()


# ============================================
# 11. ЦЕЛИ — ПОПОЛНИТЬ
# ============================================

@router.callback_query(F.data.startswith("goal_deposit_"))
async def goal_deposit(callback: CallbackQuery, state: FSMContext):
    """Начать пополнение цели"""
    await callback.answer()
    goal_id = int(callback.data.split("_")[2])
    await state.update_data(goal_id=goal_id)
    await callback.message.edit_reply_markup(reply_markup=None)
    await callback.message.answer(
        "💰 Введите сумму для пополнения цели:"
    )
    await state.set_state(GoalActionStates.waiting_amount)


@router.message(GoalActionStates.waiting_amount)
async def process_goal_deposit(message: Message, state: FSMContext):
    """Обработка суммы пополнения цели"""
    try:
        amount = int(message.text)
        if amount <= 0:
            await message.answer("❌ Сумма должна быть больше 0. Введите число:")
            return
    except ValueError:
        await message.answer("❌ Введите число:")
        return

    data = await state.get_data()
    goal_id = data['goal_id']

    new_amount = add_money_to_goal(goal_id, amount)
    goal = get_goal_by_id(goal_id)

    await message.answer(
        f"✅ Цель <b>«{goal.name}»</b> пополнена на {amount} ₽!\n"
        f"💰 Текущий баланс: {new_amount} / {goal.target_amount} ₽"
    )
    await state.clear()


# ============================================
# 12. ЦЕЛИ — ЗАВЕРШИТЬ
# ============================================

@router.callback_query(F.data.startswith("goal_complete_"))
async def goal_complete(callback: CallbackQuery):
    """Завершить цель вручную"""
    await callback.answer()
    goal_id = int(callback.data.split("_")[2])

    if complete_goal_manually(goal_id):
        goal = get_goal_by_id(goal_id)
        await callback.message.edit_reply_markup(reply_markup=None)
        await callback.message.answer(
            f"🎉 Цель <b>«{goal.name}»</b> завершена!\n"
            f"💰 Итог: {goal.current_amount} / {goal.target_amount} ₽"
        )
    else:
        await callback.message.answer("❌ Ошибка при завершении цели")


# ============================================
# 13. ЦЕЛИ — УДАЛИТЬ
# ============================================

@router.callback_query(F.data.startswith("goal_delete_"))
async def goal_delete(callback: CallbackQuery):
    """Удалить цель"""
    await callback.answer()
    goal_id = int(callback.data.split("_")[2])
    goal = get_goal_by_id(goal_id)

    if delete_goal(goal_id):
        await callback.message.edit_reply_markup(reply_markup=None)
        await callback.message.answer(
            f"🗑️ Цель <b>«{goal.name}»</b> удалена."
        )
    else:
        await callback.message.answer("❌ Ошибка при удалении цели")


# ============================================
# 14. ИСТОРИЯ ТРАНЗАКЦИЙ
# ============================================

@router.callback_query(F.data == "transaction_history")
async def show_accounts_for_history(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await callback.message.edit_reply_markup(reply_markup=None)

    accounts = get_accounts_by_type()

    if not accounts:
        await callback.message.answer(
            "❌ У вас нет ни одного счёта. Сначала добавьте счёт через 'Добавить счёт'.",
            reply_markup=get_finances_back_button()
        )
        return

    rows = []
    for acc in accounts:
        rows.append([
            InlineKeyboardButton(
                text=f"{acc.name} ({acc.balance} {acc.currency})",
                callback_data=f"history_account_{acc.id}"
            )
        ])
    rows.append([
        InlineKeyboardButton(text="◀️ Назад", callback_data="finances_back_to_menu")
    ])

    keyboard = InlineKeyboardMarkup(inline_keyboard=rows)

    await callback.message.answer(
        "📜 Выберите счёт для просмотра истории транзакций:",
        reply_markup=keyboard
    )
    await state.set_state(SelectStates.selecting_account)


@router.callback_query(SelectStates.selecting_account, F.data.startswith("history_account_"))
async def show_transaction_history(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    account_id = int(callback.data.split("_")[2])
    account = get_account_by_id(account_id)

    if not account:
        await callback.message.answer("❌ Счёт не найден")
        await state.clear()
        return

    transactions = get_transactions_by_account(account_id)

    if not transactions:
        await callback.message.edit_reply_markup(reply_markup=None)
        await callback.message.answer(
            f"📜 <b>История транзакций</b>\n\n"
            f"Счёт: {account.name}\n"
            f"Транзакций пока нет.",
            reply_markup=get_finances_back_button()
        )
        await state.clear()
        return

    text = f"📜 <b>История транзакций</b>\n\n"
    text += f"🏦 Счёт: {account.name}\n"
    text += f"💰 Текущий баланс: {account.balance} {account.currency}\n\n"
    text += "<b>Последние операции:</b>\n"

    for t in transactions[-10:]:
        date = t.transaction_date.strftime("%d.%m.%Y %H:%M")
        if t.transaction_type == "income":
            sign = "+"
            emoji = "➕"
        else:
            sign = "-"
            emoji = "➖"

        text += f"{emoji} {date} | {sign}{t.amount} ₽"
        if t.description:
            text += f" | {t.description}"
        text += "\n"

    await callback.message.edit_reply_markup(reply_markup=None)
    await callback.message.answer(
        text,
        reply_markup=get_finances_back_button()
    )
    await state.clear()



























