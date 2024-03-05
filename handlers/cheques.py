from aiogram import Router
from dbs import udb
from keyboards.smallkbs import get_accept_cheque_kb, get_back_cheque_kb
from utils.settings import ChequesStates, bot
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from bot import config

router = Router()


@router.message(ChequesStates.getAmount)
async def getAmount(message: Message, state: FSMContext):
    data = await state.get_data()
    try:
        await message.delete()
        w = data.get('errmsg')
        await bot.delete_message(chat_id=w[1], message_id=w[0])
    except:
        pass
    token = data.get('token')
    amount = message.text
    user_balance = udb.get_balance(message.from_user.id)
    token_balance = float(user_balance.get(token)) + (config.CHEQUES_FEE if token == 'TON' else 0)
    try:
        if 0 < float(amount) <= token_balance:
            if float(user_balance.get('TON')) > config.CHEQUES_FEE:
                await state.set_state(ChequesStates.acceptCheque)
                msg = data.get('msg')
                await state.update_data(cheqamount=amount)
                await bot.edit_message_text(text=f'Cоздать  персональный чека на сумму {amount} {token}?', chat_id=msg[1], message_id=msg[0], reply_markup=get_accept_cheque_kb())
            else:
                w = await message.answer(f"❌ Недостаточно TON для создания чека\nТребуется TON:{config.CHEQUES_FEE}\nУ вас TON:{user_balance.get('TON')}",
                                         reply_markup=get_back_cheque_kb())
                await state.update_data(errmsg=(w.message_id, w.chat.id))
        else:
            w = await message.answer("❌ Недостаточно средств или некорректная сумма. Попробуйте еще", reply_markup=get_back_cheque_kb())
            await state.update_data(errmsg=(w.message_id, w.chat.id))
    except:
        w = await message.answer("❌ Некорректная сумма. Попробуйте еще", reply_markup=get_back_cheque_kb())
        await state.update_data(errmsg=(w.message_id, w.chat.id))