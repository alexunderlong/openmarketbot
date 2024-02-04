from aiogram import Router
from aiogram.enums import ParseMode
from aiogram.exceptions import TelegramBadRequest
from aiogram.fsm.context import FSMContext
from aiogram.types import Message


from bot import config
from dbs import udb
from keyboards.smallkbs import get_backbtn_kb, get_accept_addr_kb
from utils.settings import WithdrawStates

router = Router()


@router.message(WithdrawStates.getsum)
async def getsum(message: Message, state: FSMContext):
    await message.delete()
    data = await state.get_data()
    msg = data.get('msg')
    try:
        txt = float(message.text)

        if txt != 0:
            max = udb.get_balance(message.from_user.id)[0] - config.WITHDRAW_FEE
            if txt <= max:
                await msg.edit_text("Введите кошелек для вывода:\n", reply_markup=get_backbtn_kb())
                await state.update_data(sum=txt)
                await state.set_state(WithdrawStates.getaddr)
            else:
                try:
                    await msg.edit_text("Недостаточно средств\n"
                                    "Введите сумму для вывода:", reply_markup=get_backbtn_kb())
                except TelegramBadRequest:
                    pass
        else:
            await msg.edit_text("Некорректная сумма\nВведите сумму для вывода:", reply_markup=get_backbtn_kb())
    except ValueError:
        await msg.edit_text("Некорректная сумма\nВведите сумму для вывода:", reply_markup=get_backbtn_kb())


@router.message(WithdrawStates.getaddr)
async def getaddr(message: Message, state: FSMContext):
    data = await state.get_data()
    addr = message.text
    sum = data.get('sum')
    await state.update_data(addr=addr)
    msg = data.get('msg')
    await message.delete()
    await msg.edit_text("Вы подтверждаете перевод\n"
                         "ваших средств на адрес:\n"
                         f"<code>{addr}</code>\n"
                         f"в размере {sum} OPEN?\n\n"
                         f"Если был введен неверный\n"
                         f"кошелек средства будут утеряны", reply_markup=get_accept_addr_kb(), parse_mode=ParseMode.HTML)
