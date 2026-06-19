from aiogram import Router, F
from aiogram.filters import Command, CommandStart
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from keyboards.tasks import get_tasks_main_keyboard
from keyboards.finances import get_finances_main_keyboard
from keyboards.investments import get_investments_main_keyboard

router = Router()

@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    await state.clear()
    user_name = message.from_user.first_name
    welcome_text = f"Привет, {user_name}!\n\nДобро пожаловать в бота!"
    await message.answer(welcome_text)

@router.message(Command("tasks"))
async def cmd_tasks(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(
        "📋 <b>Управление задачами</b>\n\nВыбери действие:",
        reply_markup=get_tasks_main_keyboard()
    )

@router.message(Command("finances"))
async def cmd_finances(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(
        "💰 <b>Управление финансами</b>\n\nВыбери действие:",
        reply_markup=get_finances_main_keyboard()
    )

@router.message(Command("investments"))
async def cmd_investments(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(
        "📈 <b>Управление инвестициями</b>\n\nВыбери действие:",
        reply_markup=get_investments_main_keyboard()
    )

@router.message(Command("help"))
async def cmd_help(message: Message):
    await message.answer("Справка: /tasks, /finances, /investments")

@router.callback_query(F.data == "back_to_main")
async def back_to_main(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.answer()
    await callback.message.delete()
    await cmd_start(callback.message, state)
