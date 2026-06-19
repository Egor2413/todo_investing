from aiogram import Router, F
from aiogram.filters import Command, CommandStart
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

router = Router()

@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    """Приветствие при старте"""
    await state.clear()

    user_name = message.from_user.first_name

    welcome_text = f"""
    Привет, {user_name}!

Добро пожаловать в твоего личного помощника!

📋 С его помощью ты можешь:
• ✅ Ставить задачи и получать баллы за их выполнение
• 💰 Управлять финансами и следить за бюджетом
• 📈 Отслеживать инвестиции и криптовалюты

👇 Просто выбери нужный раздел через меню (кнопка ≡)

📌 Доступные команды:
/tasks — задачи и баллы
/finances — финансы и счета
/investments — инвестиции и портфель
/help — помощь
"""

    await message.answer(welcome_text)

@router.message(Command("tasks"))
async def cmd_tasks(message: Message, state: FSMContext):
    """Переход в раздел 'задачи' """
    await state.clear()
    await message.answer(
        "Раздел «Задачи»\n\n"
        "Здесь ты сможешь:\n"
        "• Добавлять задачи\n"
        "• Отмечать их выполнение\n"
        "• Получать баллы\n"
        "• Смотреть статистику\n\n"
    )

@router.message(Command("finances"))
async def cmd_finances(message: Message, state: FSMContext):
    """Переход в раздел 'финансы' """
    await state.clear()
    await message.answer(
        "Раздел «Финансы»\n\n"
        "Здесь ты сможешь:\n"
        "• Вести учёт доходов и расходов\n"
        "• Управлять счетами\n"
        "• Ставить финансовые цели\n\n"
    )

@router.message(Command("investments"))
async def cmd_finances(message: Message, state: FSMContext):
    """Переход в раздел 'инвестиции' """
    await state.clear()
    await message.answer(
        "Раздел «Инвестиции»\n\n"
        "Здесь ты сможешь:\n"
        "• Отслеживать портфель акций и криптовалют\n"
        "• Анализировать риски\n"
        "• Смотреть доходность\n\n"
    )

@router.message(Command("help"))
async def cmd_help(message: Message):
    """Справка по командам"""
    help_text = """
📖 <b>Справка по командам</b>

📋 <b>/tasks</b> — задачи и баллы
   Добавляй задачи, отмечай выполнение, получай баллы

💰 <b>/finances</b> — финансы и счета
   Управляй счетами, доходами и расходами, ставь цели

📈 <b>/investments</b> — инвестиции и портфель
   Отслеживай акции, криптовалюты, риски и доходность

❓ <b>/help</b> — эта справка

💡 <b>Совет:</b> Все команды доступны через меню (кнопка ≡ внизу экрана)
"""
    await message.answer(help_text)


@router.callback_query(F.data == "back_to_main")
async def back_to_main(callback: CallbackQuery, state: FSMContext):
    """Возврат в главное меню"""
    await state.clear()
    await callback.answer()
    await callback.message.delete()
    await cmd_start(callback.message, state)