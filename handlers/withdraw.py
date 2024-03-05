from aiogram import Router
from aiogram.enums import ParseMode
from aiogram.exceptions import TelegramBadRequest
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from utils.settings import bot
from bot import config
from dbs import udb
from keyboards.smallkbs import get_backbtn_kb, get_accept_addr_kb
from utils.getcourcebydior import readcource
from utils.settings import WithdrawStates

router = Router()


@router.message(WithdrawStates.getsum)
async def getsum(message: Message, state: FSMContext):
    await message.delete()
    data = await state.get_data()
    msg = data.get('msg')
    token = data.get('token')
    cource = readcource()
    try:
        txt = float(message.text)
        fee = float(1 if token == 'TON' else cource.get(token))
        if txt != 0:
            max = udb.get_balance(message.from_user.id).get(token) - (config.WITHDRAW_FEE/fee)
            if 0 < txt <= max:
                await bot.edit_message_text(text="Введите кошелек для вывода:\n", reply_markup=get_backbtn_kb(), message_id=msg[0], chat_id=msg[1])
                await state.update_data(sum=txt)
                await state.set_state(WithdrawStates.getaddr)
            else:
                try:
                    await bot.edit_message_text(text="Некорректная сумма\n"
                                    "Введите сумму для вывода:", reply_markup=get_backbtn_kb(), message_id=msg[0], chat_id=msg[1])
                except TelegramBadRequest:
                    pass
        else:
            await bot.edit_message_text(text="Некорректная сумма\nВведите сумму для вывода:", reply_markup=get_backbtn_kb(), message_id=msg[0], chat_id=msg[1])
    except ValueError:
        await bot.edit_message_text(text="Некорректная сумма\nВведите сумму для вывода:", reply_markup=get_backbtn_kb(), message_id=msg[0], chat_id=msg[1])


@router.message(WithdrawStates.getaddr)
async def getaddr(message: Message, state: FSMContext):
    data = await state.get_data()
    addr = message.text
    sum = data.get('sum')
    await state.update_data(addr=addr)
    msg = data.get('msg')
    token = data.get('token')
    await message.delete()
    cource = readcource()
    fee = float(1 if token == 'TON' else cource.get(token))
    await bot.edit_message_text(text="Вы подтверждаете перевод\n"
                         "ваших средств на адрес:\n"
                         f"<code>{addr}</code>\n"
                         f"в размере {sum:.2f} {token}?\n\n"
                         f"Если был введен неверный\n"
                         f"кошелек средства будут утеряны", reply_markup=get_accept_addr_kb(), parse_mode=ParseMode.HTML, message_id=msg[0], chat_id=msg[1])
