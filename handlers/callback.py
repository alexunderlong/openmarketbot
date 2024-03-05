from aiogram import Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

import keyboards.smallkbs
from dbs import udb
from handlers import start
from handlers.callbackdefs import callbalance, market, TKsendnum, offers_process, offer_process, mydeals, ActiveDeals, \
    del_deal, withdraw, calltransfer, calldep, market_makedeal, market_CorB, deal_start, offer_accept, deal_decline, \
    sendnum, TK_accept_trans, MK_accept_trans, MK_accept_deal, TK_accept_deal, dealpayed, choosetokenfordep, \
    choosetokenforwd, banks_process, MK_give_num, chequemain, pchequetoken, pchequeamount, makepcheque, getcheques, \
    cheqinfo, cheqdel, allmydeals, myinactivedeals, dealinfo, todeal

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
        await choosetokenfordep(message)
    elif data == 'cheque':
        await chequemain(call, state)
    elif data == 'personalcheque':
        await pchequetoken(call)
    elif data == 'makepcheque':
        data = await state.get_data()
        user_balance = udb.get_balance(call.from_user.id)
        token = float(user_balance.get(data.get('token')))
        if float(data.get('cheqamount')) <= token:
            await makepcheque(call, state)
        else:
            await call.message.edit_text('Недостаточно средств', reply_markup=keyboards.smallkbs.get_back_cheque_kb())
    elif bool(call.data.startswith('cheque:')):
        await pchequeamount(call, state)
    elif bool(call.data.startswith('cheqinfo:')):
        await cheqinfo(call)
    elif bool(call.data.startswith('delcheq:')):
        await cheqdel(call)
    elif data == 'getcheques':
        await getcheques(call)
    elif data == 'transfer':
        await calltransfer(uid, message, state)
    elif data == 'withdraw':
        await choosetokenforwd(message)
    elif data == 'market':
        await state.set_state(state=None)
        state_data = await state.get_data()
        await state.set_data({'msgid': state_data.get('msgid'), 'chatid': state_data.get('chatid')})
        await market(message, state)
    elif data == 'makedeal':
        await market_makedeal(message, state)
    elif data == 'payed':
        await dealpayed(call, state)
    elif data == 'buy' or data == 'sell':
        await market_CorB(uid, message, state, data)
    elif data == 'mydeals':
        await mydeals(uid, message)
    elif data == 'unactive':
        await myinactivedeals(uid, message)
    elif data == 'allmydeals':
        await allmydeals(uid, message)
    elif bool(call.data.startswith('bank_id:')):
        bankid = int(call.data.replace("bank_id:", ""))
        state_data = await state.get_data()
        if state_data.get('maker'):
            await MK_give_num(state=state, message=message, bankid=bankid)
        else:
            await ActiveDeals(message, state, bankid)
    elif bool(call.data.startswith('dealinfo:')):
        await dealinfo(call)
    elif bool(call.data.startswith('todeal:')):
        await todeal(call, state)
    elif bool(call.data.startswith("accept:")):
        await offer_accept(call, state)
    elif bool(call.data.startswith("decline:")):
        await deal_decline(call, state)
    elif data == 'sendnum':
        await sendnum(state, call)
    elif bool(call.data.startswith("TK_accept_trans:")):
        await TK_accept_trans(call)
    elif bool(call.data.startswith("dep:")):
        await calldep(uid, message, call)
    elif bool(call.data.startswith("MK_accept_trans:")):
        await MK_accept_trans(call)
    elif bool(call.data.startswith("MK_accept_deal:")):
        await MK_accept_deal(call)
    elif bool(call.data.startswith("TK_accept_deal:")):
        await TK_accept_deal(call)
    elif bool(call.data.startswith("TKsendnum:")):
        await TKsendnum(call, state)
    elif call.data.startswith("wd:"):
        await withdraw(uid, state, call)
    elif bool(call.data.endswith("_banks")):
        await banks_process(call, state)
    if await state.get_state() == "MarketStates:ActiveDeals":
        if bool(call.data.endswith("_offers")):
            await offers_process(call, state)
        elif bool(call.data.startswith("offer_id:")):
            await offer_process(call, state)
        elif bool(call.data.startswith("startdeal:")):
            await deal_start(call, state)
    if bool(call.data.startswith("del:")):
        await del_deal(call)
