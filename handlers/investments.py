from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from datetime import datetime, timedelta

from keyboards.investments import (
    get_investments_main_keyboard,
    get_investments_back_button,
    get_asset_type_keyboard,
    get_asset_confirm_keyboard,
    get_asset_choice_keyboard,
    get_snapshot_selection_keyboard
)
from states.investments import (
    AddAssetStates,
    UpdatePriceStates,
    SellAssetStates
)
from database.db import (
    add_asset,
    get_portfolio,
    get_asset_by_id,
    update_asset_price,
    sell_asset,
    get_portfolio_value,
    get_portfolio_risk,
    create_monthly_snapshot,
    get_current_quarter,
    get_next_quarter_start,
    is_snapshot_window_open,
    get_snapshot_history,
    get_snapshot_by_date,
    check_asset_exists,
    get_asset_by_name,
    add_to_existing_asset,
    get_portfolio_profit
)

router = Router()


# ============================================
# 1. КОМАНДА /investments
# ============================================
@router.message(Command("investments"))
async def cmd_investments(message: Message, state: FSMContext):
    """Показать главное меню инвестиций"""
    await state.clear()
    await message.answer(
        "📈 <b>Управление инвестициями</b>\n\n"
        "Выбери действие:",
        reply_markup=get_investments_main_keyboard()
    )


# ============================================
# 2. ВОЗВРАТ В ГЛАВНОЕ МЕНЮ
# ============================================
@router.callback_query(F.data == "investments_back_to_menu")
async def back_to_investments_menu(callback: CallbackQuery, state: FSMContext):
    """Вернуться в главное меню инвестиций"""
    await state.clear()
    await callback.answer()
    await callback.message.edit_reply_markup(reply_markup=None)
    await callback.message.answer(
        "📈 <b>Управление инвестициями</b>\n\nВыбери действие:",
        reply_markup=get_investments_main_keyboard()
    )


# ============================================
# 3. ПОРТФЕЛЬ
# ============================================
@router.callback_query(F.data == "portfolio_show")
async def show_portfolio(callback: CallbackQuery):
    await callback.answer()
    await callback.message.edit_reply_markup(reply_markup=None)

    assets = get_portfolio()

    if not assets:
        await callback.message.answer(
            "📊 Портфель пуст. Добавьте актив через 'Добавить актив'.",
            reply_markup=get_investments_back_button()
        )
        return

    total_value = get_portfolio_value()

    text = "📊 <b>Твой портфель</b>\n\n"

    # Группируем по типам
    stocks = [a for a in assets if a.security_type == "stock"]
    crypto = [a for a in assets if a.security_type == "crypto"]
    etfs = [a for a in assets if a.security_type == "etf"]
    others = [a for a in assets if a.security_type not in ["stock", "crypto", "etf"]]

    if stocks:
        text += "📈 <b>Акции:</b>\n"
        for a in stocks:
            text += f"   • {a.name}: {a.quantity} шт. × {a.value}₽ = {a.quantity * a.value}₽\n"
        text += "\n"

    if crypto:
        text += "🪙 <b>Криптовалюты:</b>\n"
        for a in crypto:
            text += f"   • {a.name}: {a.quantity} × {a.value}₽ = {a.quantity * a.value}₽\n"
        text += "\n"

    if etfs:
        text += "📊 <b>ETF:</b>\n"
        for a in etfs:
            text += f"   • {a.name}: {a.quantity} шт. × {a.value}₽ = {a.quantity * a.value}₽\n"
        text += "\n"

    if others:
        text += "💎 <b>Другое:</b>\n"
        for a in others:
            text += f"   • {a.name}: {a.quantity} × {a.value}₽ = {a.quantity * a.value}₽\n"
        text += "\n"

    text += f"💰 <b>Общая стоимость:</b> {total_value:,.0f} ₽"

    await callback.message.answer(text, reply_markup=get_investments_back_button())


# ============================================
# 4. ДОБАВЛЕНИЕ АКТИВА (НОВАЯ ЛОГИКА)
# ============================================

@router.callback_query(F.data == "add_asset")
async def start_add_asset(callback: CallbackQuery, state: FSMContext):
    """Начать добавление актива (ввод названия)"""
    await callback.answer()
    await callback.message.edit_reply_markup(reply_markup=None)
    await callback.message.answer("Введите название актива (например, 'Sberbank', 'Bitcoin'):")
    await state.set_state(AddAssetStates.waiting_name)


@router.message(AddAssetStates.waiting_name)
async def process_asset_name(message: Message, state: FSMContext):
    """Обработка названия актива. Проверка дубликата."""
    name = message.text.strip()
    await state.update_data(name=name)

    # Проверяем, есть ли актив с таким названием
    if check_asset_exists(name):
        # Есть дубликат → предлагаем выбор
        await message.answer(
            f"⚠️ Актив <b>«{name}»</b> уже существует в портфеле.\n\n"
            "Что делаем?",
            reply_markup=get_asset_choice_keyboard(name)
        )
        await state.set_state(AddAssetStates.waiting_choice)
    else:
        # Новый актив → запрашиваем тип
        await message.answer(
            "🆕 Новый актив.\n\nВыберите тип:",
            reply_markup=get_asset_type_keyboard()
        )
        await state.set_state(AddAssetStates.waiting_type)


@router.callback_query(AddAssetStates.waiting_choice, F.data.startswith("add_to_existing_"))
async def add_to_existing_asset_handler(callback: CallbackQuery, state: FSMContext):
    """Добавить к существующему активу"""
    await callback.answer()
    asset_name = callback.data.replace("add_to_existing_", "")
    asset = get_asset_by_name(asset_name)

    if not asset:
        await callback.message.answer("❌ Актив не найден. Попробуйте снова.")
        await state.clear()
        return

    await state.update_data(existing_asset_id=asset.id)
    await callback.message.edit_reply_markup(reply_markup=None)
    await callback.message.answer(
        f"➕ Добавление к <b>«{asset_name}»</b>\n\n"
        f"Текущее количество: {asset.quantity}\n"
        f"Текущая средняя цена: {asset.value} ₽\n\n"
        "Введите количество для добавления:"
    )
    await state.set_state(AddAssetStates.waiting_quantity)


@router.callback_query(AddAssetStates.waiting_choice, F.data == "create_new_asset")
async def create_new_asset_handler(callback: CallbackQuery, state: FSMContext):
    """Создать новый актив (обычный поток)"""
    await callback.answer()
    await callback.message.edit_reply_markup(reply_markup=None)
    await callback.message.answer(
        "🆕 Создание нового актива.\n\nВыберите тип:",
        reply_markup=get_asset_type_keyboard()
    )
    await state.set_state(AddAssetStates.waiting_type)


@router.callback_query(AddAssetStates.waiting_type, F.data.startswith("asset_type_"))
async def process_asset_type(callback: CallbackQuery, state: FSMContext):
    """Обработка типа актива"""
    await callback.answer()

    type_map = {
        "asset_type_stock": "stock",
        "asset_type_crypto": "crypto",
        "asset_type_etf": "etf",
        "asset_type_other": "other"
    }
    asset_type = type_map.get(callback.data, "other")
    await state.update_data(asset_type=asset_type)

    await callback.message.edit_reply_markup(reply_markup=None)
    await callback.message.answer("Введите количество (например, 10, 0.5):")
    await state.set_state(AddAssetStates.waiting_quantity)


@router.message(AddAssetStates.waiting_quantity)
async def process_asset_quantity(message: Message, state: FSMContext):
    """Обработка количества"""
    try:
        quantity = float(message.text.replace(",", "."))
        if quantity <= 0:
            await message.answer("❌ Количество должно быть больше 0. Введите число:")
            return
    except ValueError:
        await message.answer("❌ Введите число (например, 10 или 0.5):")
        return

    await state.update_data(quantity=quantity)
    await message.answer("Введите цену (в рублях):")
    await state.set_state(AddAssetStates.waiting_price)


@router.message(AddAssetStates.waiting_price)
async def process_asset_price(message: Message, state: FSMContext):
    """Обработка цены"""
    try:
        price = float(message.text.replace(",", "."))
        if price <= 0:
            await message.answer("❌ Цена должна быть больше 0. Введите число:")
            return
    except ValueError:
        await message.answer("❌ Введите число:")
        return

    await state.update_data(price=price)

    # Проверяем, есть ли existing_asset_id (добавление к существующему)
    data = await state.get_data()
    if data.get("existing_asset_id"):
        # Добавление к существующему → сразу сохраняем без риска
        asset_id = data["existing_asset_id"]
        new_avg_price = add_to_existing_asset(asset_id, data["quantity"], data["price"])

        asset = get_asset_by_id(asset_id)
        await message.answer(
            f"✅ Актив <b>«{asset.name}»</b> пополнен!\n\n"
            f"Новое количество: {asset.quantity}\n"
            f"Новая средняя цена: {new_avg_price:.2f} ₽\n"
            f"Общая стоимость: {asset.quantity * asset.value:.2f} ₽"
        )
        await state.clear()
    else:
        # Новый актив → запрашиваем риск
        await message.answer("Введите уровень риска (от 1 до 10, где 10 — максимальный риск):")
        await state.set_state(AddAssetStates.waiting_risk)


@router.message(AddAssetStates.waiting_risk)
async def process_asset_risk(message: Message, state: FSMContext):
    """Обработка риска (только для нового актива)"""
    try:
        risk = int(message.text)
        if risk < 1 or risk > 10:
            await message.answer("❌ Уровень риска должен быть от 1 до 10. Введите число:")
            return
    except ValueError:
        await message.answer("❌ Введите число от 1 до 10:")
        return

    data = await state.get_data()

    confirm_text = (
        f"<b>Новый актив</b>\n\n"
        f"Название: {data['name']}\n"
        f"Тип: {data['asset_type']}\n"
        f"Количество: {data['quantity']}\n"
        f"Цена: {data['price']} ₽\n"
        f"Риск: {risk}/10\n\n"
        f"Добавить?"
    )

    await state.update_data(risk=risk)
    await message.answer(confirm_text, reply_markup=get_asset_confirm_keyboard())
    await state.set_state(AddAssetStates.waiting_confirm)


@router.callback_query(AddAssetStates.waiting_confirm, F.data == "confirm_asset_yes")
async def confirm_add_asset(callback: CallbackQuery, state: FSMContext):
    """Подтверждение добавления нового актива"""
    await callback.answer()
    data = await state.get_data()

    asset_id = add_asset(
        name=data['name'],
        asset_type=data['asset_type'],
        quantity=data['quantity'],
        price=data['price'],
        risk_level=data['risk']
    )

    await callback.message.edit_reply_markup(reply_markup=None)
    await callback.message.answer(
        f"✅ Актив <b>«{data['name']}»</b> добавлен в портфель!\n"
        f"Количество: {data['quantity']}\n"
        f"Цена: {data['price']} ₽\n"
        f"Риск: {data['risk']}/10"
    )
    await state.clear()


@router.callback_query(AddAssetStates.waiting_confirm, F.data == "confirm_asset_no")
async def cancel_add_asset(callback: CallbackQuery, state: FSMContext):
    """Отмена добавления актива"""
    await callback.answer()
    await callback.message.edit_reply_markup(reply_markup=None)
    await callback.message.answer("❌ Добавление актива отменено.")
    await state.clear()
    await cmd_investments(callback.message, state)


# ============================================
# 5. СНИМКИ
# ============================================

@router.callback_query(F.data == "make_snapshot")
async def make_snapshot(callback: CallbackQuery):
    """Создать квартальный снимок портфеля (только в окне)"""
    await callback.answer()
    await callback.message.edit_reply_markup(reply_markup=None)

    if not is_snapshot_window_open():
        next_start = get_next_quarter_start()
        next_end = next_start + timedelta(days=9)
        await callback.message.answer(
            f"❌ Окно создания снимка закрыто.\n\n"
            f"Следующее окно: {next_start.strftime('%d.%m.%Y')} — {next_end.strftime('%d.%m.%Y')}"
        )
        return

    now = datetime.now()
    year, quarter = get_current_quarter()
    count = create_monthly_snapshot(year, now.month)

    await callback.message.answer(
        f"📸 Квартальный снимок создан!\n\n"
        f"📅 {year}-Q{quarter}\n"
        f"📊 Сохранено активов: {count}\n\n"
        f"Следующий снимок: Q{quarter + 1 if quarter < 4 else 1} {year if quarter < 4 else year + 1}"
    )


# ============================================
# 6. ИСТОРИЯ СНИМКОВ (СТОИМОСТЬ ПОРТФЕЛЯ)
# ============================================

@router.callback_query(F.data == "snapshot_history")
async def snapshot_history(callback: CallbackQuery):
    """Показать историю снимков"""
    await callback.answer()
    await callback.message.edit_reply_markup(reply_markup=None)

    snapshots = get_snapshot_history()

    if not snapshots:
        await callback.message.answer(
            "📊 История снимков пуста.\n\n"
            "Создай первый снимок в разделе «Создать снимок» (окно 1–10 числа).",
            reply_markup=get_investments_back_button()
        )
        return

    text = "📊 <b>История стоимости портфеля</b>\n\n"
    for snap in snapshots[:10]:
        quarter = (snap.month - 1) // 3 + 1
        text += f"📅 <b>{snap.year}-Q{quarter}</b> ({snap.month}.{snap.year})\n"
        text += f"   💰 Стоимость: {snap.total_value:,.0f} ₽\n"
        text += f"   📈 Цена: {snap.price} ₽\n\n"

    await callback.message.answer(text, reply_markup=get_investments_back_button())


# ============================================
# 7. ДОХОДНОСТЬ (ОСТАВЛЯЕМ, НО НЕ ИСПОЛЬЗУЕМ)
# ============================================

@router.callback_query(F.data == "portfolio_profit")
async def show_profit(callback: CallbackQuery):
    await callback.answer()
    await callback.message.edit_reply_markup(reply_markup=None)

    assets = get_portfolio()

    if not assets:
        await callback.message.answer(
            "💰 Портфель пуст. Добавьте актив через 'Добавить актив'.",
            reply_markup=get_investments_back_button()
        )
        return

    total_value = get_portfolio_value()

    text = "💰 <b>Доходность портфеля</b>\n\n"

    for a in assets:
        if a.avg_dividents and a.avg_dividents > 0:
            profit_percent = ((a.value - a.avg_dividents) / a.avg_dividents) * 100
            profit_rub = (a.value - a.avg_dividents) * a.quantity
        else:
            profit_percent = 0
            profit_rub = 0

        if profit_percent >= 0:
            text += f"📈 <b>{a.name}</b>: +{profit_percent:.1f}% (+{profit_rub:,.0f}₽)\n"
        else:
            text += f"📉 <b>{a.name}</b>: {profit_percent:.1f}% ({profit_rub:,.0f}₽)\n"

    text += f"\n💰 <b>Общая стоимость портфеля:</b> {total_value:,.0f} ₽"

    await callback.message.answer(text, reply_markup=get_investments_back_button())


# ============================================
# 8. РИСКИ (ОСТАВЛЯЕМ, НО НЕ ИСПОЛЬЗУЕМ)
# ============================================

@router.callback_query(F.data == "portfolio_risk")
async def show_risk(callback: CallbackQuery):
    await callback.answer()
    await callback.message.edit_reply_markup(reply_markup=None)

    assets = get_portfolio()

    if not assets:
        await callback.message.answer(
            "📉 Портфель пуст. Добавьте актив через 'Добавить актив'.",
            reply_markup=get_investments_back_button()
        )
        return

    risk_data = get_portfolio_risk()

    text = "📉 <b>Оценка рисков портфеля</b>\n\n"
    text += f"📊 <b>Средний риск:</b> {risk_data['avg_risk']:.1f}/10\n\n"

    text += "<b>По типам активов:</b>\n"
    type_names = {
        "stock": "📈 Акции",
        "crypto": "🪙 Криптовалюты",
        "etf": "📊 ETF",
        "other": "💎 Другое"
    }

    for t, risk in risk_data['by_type'].items():
        name = type_names.get(t, t)
        risk_bar = "🔴" * int(risk) + "⚪" * (10 - int(risk))
        text += f"{name}: {risk_bar} {risk:.1f}/10\n"

    text += "\n<b>Риск по каждому активу:</b>\n"
    for a in assets:
        risk_bar = "🔴" * a.risk_level + "⚪" * (10 - a.risk_level)
        text += f"• {a.name}: {risk_bar} {a.risk_level}/10\n"

    await callback.message.answer(text, reply_markup=get_investments_back_button())