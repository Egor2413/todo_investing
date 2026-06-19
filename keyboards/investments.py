from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

# ============================================
# 1. ГЛАВНОЕ МЕНЮ ИНВЕСТИЦИЙ
# ============================================

def get_investments_main_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура главного меню раздела Инвестиции"""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="📊 Портфель", callback_data="portfolio_show"),
                InlineKeyboardButton(text="➕ Добавить актив", callback_data="add_asset")
            ],
            [
                InlineKeyboardButton(text="📸 Создать снимок", callback_data="make_snapshot"),
                InlineKeyboardButton(text="💰 Стоимость портфеля", callback_data="snapshot_history")
            ],
            [
                InlineKeyboardButton(text="📉 Риски", callback_data="portfolio_risk")
            ],
            [
                InlineKeyboardButton(text="◀️ В главное меню", callback_data="back_to_main")
            ]
        ]
    )


# ============================================
# 2. КНОПКА "НАЗАД" (общая)
# ============================================

def get_investments_back_button() -> InlineKeyboardMarkup:
    """Простая кнопка назад в главное меню инвестиций"""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="◀️ Назад", callback_data="investments_back_to_menu")
            ]
        ]
    )


# ============================================
# 3. ВЫБОР ТИПА АКТИВА (для добавления)
# ============================================

def get_asset_type_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура выбора типа актива"""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="📈 Акции", callback_data="asset_type_stock"),
                InlineKeyboardButton(text="🪙 Криптовалюта", callback_data="asset_type_crypto")
            ],
            [
                InlineKeyboardButton(text="📊 ETF", callback_data="asset_type_etf"),
                InlineKeyboardButton(text="💎 Другое", callback_data="asset_type_other")
            ],
            [
                InlineKeyboardButton(text="◀️ Назад", callback_data="investments_back_to_menu")
            ]
        ]
    )


# ============================================
# 4. ВЫБОР ДЕЙСТВИЯ ПРИ ДУБЛИКАТЕ
# ============================================

def get_asset_choice_keyboard(asset_name: str) -> InlineKeyboardMarkup:
    """Клавиатура выбора: добавить к существующему или создать новый"""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=f"➕ Добавить к «{asset_name}»",
                    callback_data=f"add_to_existing_{asset_name}"
                )
            ],
            [
                InlineKeyboardButton(
                    text="🆕 Создать новый",
                    callback_data="create_new_asset"
                )
            ],
            [
                InlineKeyboardButton(text="◀️ Назад", callback_data="investments_back_to_menu")
            ]
        ]
    )


# ============================================
# 5. КЛАВИАТУРА ПОДТВЕРЖДЕНИЯ
# ============================================

def get_asset_confirm_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура подтверждения добавления актива"""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="✅ Да, добавить", callback_data="confirm_asset_yes"),
                InlineKeyboardButton(text="❌ Нет, отмена", callback_data="confirm_asset_no")
            ]
        ]
    )


# ============================================
# 6. КЛАВИАТУРА ВЫБОРА СНИМКА (для истории)
# ============================================

def get_snapshot_selection_keyboard(snapshots: list) -> InlineKeyboardMarkup:
    """Клавиатура выбора снимка из истории"""
    rows = []
    for snap in snapshots:
        quarter = (snap.month - 1) // 3 + 1
        rows.append([
            InlineKeyboardButton(
                text=f"📸 {snap.year}-Q{quarter} ({snap.month}.{snap.year})",
                callback_data=f"snapshot_detail_{snap.year}_{snap.month}"
            )
        ])
    rows.append([
        InlineKeyboardButton(text="◀️ Назад", callback_data="investments_back_to_menu")
    ])
    return InlineKeyboardMarkup(inline_keyboard=rows)