from aiogram import Router, F
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from bot import config
from dbs import udb
from keyboards import startkb

router = Router()
starttext = "_Здравствуйте, вас приветствует_ *OpenMarket* _- P2P бот для продажи и покупки токена_ *OPENCOIN*.\n\n"


@router.message(CommandStart())
async def command_start_handler(message: Message, state: FSMContext) -> None:
    current_state = await state.get_state()
    if current_state:
        await state.clear()
    uid = message.from_user.id

    if not udb.check_user(uid) and uid != config.BOT_ID:
        udb.add_user(uid)
    if uid == config.BOT_ID:
        await message.edit_text(text=starttext, reply_markup=startkb.get_start_kb(), parse_mode=ParseMode.MARKDOWN)
    else:
        await message.answer(text=starttext, reply_markup=startkb.get_start_kb(), parse_mode=ParseMode.MARKDOWN)
