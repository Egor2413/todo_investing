from aiogram.fsm.state import State, StatesGroup

class AddTaskStates(StatesGroup):
    """Состояния для добавления новой задачи"""
    waiting_title = State()
    waiting_due_date = State()
    waiting_value = State()
    waiting_confirm = State()
    waiting_goal = State()
    waiting_completed_month = State()

class CompleteTasksStates(StatesGroup):
    waiting_task_selection = State()

class DeleteTasksStates(StatesGroup):
    waiting_task_selection = State()
