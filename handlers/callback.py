from aiogram import Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

from handlers import start
from handlers.callbackdefs import callbalance, market, TKsendnum, offers_process, offer_process, mydeals, ActiveDeals, \
    del_deal, withdraw, calltransfer, calldep, market_makedeal, market_CorB, deal_start, offer_accept, deal_decline, \
    sendnum, TK_accept_trans, MK_accept_trans, MK_accept_deal, TK_accept_deal, dealpayed

router = Router()

@router.callback_query(lambda call: True)
async def main_callback_handler(call: CallbackQuery, state: FSMContext):
    await call.answer()
    message = call.message
    uid = call.from_user.id
    data = call.data
    if data == "start":
        await start.command_start_handler(message, state)
    elif data == 'balance':
        await callbalance(uid, call)
    elif data == 'deposit':
        await calldep(uid, message)
    elif data == 'transfer':
        await calltransfer(uid, message, state)
    elif data == 'withdraw':
        await withdraw(uid, message, state)
    elif data == 'market':
        await state.clear()
        await market(message, state)
    elif data == 'makedeal':
        await market_makedeal(message, state)
    elif data == 'payed':
        await dealpayed(call, state)
    elif data == 'buy' or data == 'sell':
        await market_CorB(uid, message, state, data)
    elif data == 'mydeals':
        await mydeals(uid, message)
    elif data == 'okey':
        await ActiveDeals(message, state)
    elif bool(call.data.startswith("accept:")):
        await offer_accept(call, state)
    elif bool(call.data.startswith("decline:")):
        await deal_decline(call, state)
    elif data == 'sendnum':
        await sendnum(state, call)
    elif bool(call.data.startswith("TK_accept_trans:")):
        await TK_accept_trans(call)
    elif bool(call.data.startswith("MK_accept_trans:")):
        await MK_accept_trans(call)
    elif bool(call.data.startswith("MK_accept_deal:")):
        await MK_accept_deal(call)
    elif bool(call.data.startswith("TK_accept_deal:")):
        await TK_accept_deal(call)
    elif bool(call.data.startswith("TKsendnum:")):
        await TKsendnum(call, state)
    else:
        data = data.split(':')
    if await state.get_state() == "MarketStates:ActiveDeals":
        if bool(call.data.endswith("_offers")):
            await offers_process(call, state)
        elif bool(call.data.startswith("offer_id:")):
            await offer_process(call, state)
        elif bool(call.data.startswith("startdeal:")):
            await deal_start(call, state)
    if bool(call.data.startswith("del:")):
        await del_deal(call)
