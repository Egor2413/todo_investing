from aiogram.fsm.state import State, StatesGroup

class AddAccountStates(StatesGroup):
    """Добавление нового счёта (4 шага)"""
    waiting_type = State()
    waiting_name = State()
    waiting_currency = State()
    waiting_balance = State()

class DepositWithdrawStates(StatesGroup):
    """Пополнение или снятие со счёта (3 шага)"""
    waiting_account = State()
    waiting_action = State()
    waiting_amount = State()

class AddGoalStates(StatesGroup):
    """Создание финансовой цели (3 шага)"""
    waiting_name = State()
    waiting_target = State()
    waiting_deadline = State()

class SelectStates(StatesGroup):
    """Выбор без ввода текста (1 шаг)"""
    selecting_type = State()
    selecting_goal = State()
    selecting_account = State()

class GoalActionStates(StatesGroup):
    """Состояния для действий с целями"""
    waiting_goal_selection = State()
    waiting_amount = State()