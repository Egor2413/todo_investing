from aiogram.fsm.state import State, StatesGroup

class AddAssetStates(StatesGroup):
    """Добавление актива (новый или к существующему)"""
    waiting_name = State()        # шаг 1: название актива
    waiting_choice = State()      # шаг 2: выбор (к существующему / новый) ← ДОБАВИТЬ
    waiting_type = State()        # шаг 3: тип (акции/крипта/etf)
    waiting_quantity = State()    # шаг 4: количество
    waiting_price = State()       # шаг 5: цена
    waiting_risk = State()        # шаг 6: уровень риска (1-10) (для нового)
    waiting_confirm = State()     # шаг 7: подтверждение

class UpdatePriceStates(StatesGroup):
    """Обновление цены актива (2 шага)"""
    waiting_asset = State()       # шаг 1: выбор актива
    waiting_new_price = State()   # шаг 2: новая цена

class SellAssetStates(StatesGroup):
    """Продажа актива (2 шага)"""
    waiting_asset = State()       # шаг 1: выбор актива
    waiting_quantity = State()    # шаг 2: количество для продажи