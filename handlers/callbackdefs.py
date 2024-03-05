import json
from datetime import datetime
from types import NoneType
from dbs import chequesdb as chqdb
from aiogram.enums import ParseMode
from aiogram.exceptions import TelegramBadRequest
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from aiogram.utils.deep_linking import create_deep_link
from aiogram import types
import keyboards.choosekb
from bot import config
from dbs import udb, dealsdb
from keyboards.bankskb import banks_kb
from keyboards.marketkb import get_market_kb
from keyboards.mydealskb import get_my_deals_kb, get_my_all_deals_kb, get_all_unactive_deals_kb
from keyboards.offerskb import offers_kb
import keyboards.smallkbs as skb
from utils.getcourcebydior import readcource
from utils.settings import bot, ChequesStates
from utils import Wallet
from utils.settings import MarketStates, WithdrawStates
from utils.getsalt import getsalt


async def callbalance(uid, call: types.CallbackQuery):
    tcource = readcource()
    user_balance = udb.get_balance(uid)
    user_lock = udb.get_lock(uid)
    if user_lock == json.dumps({"TON": 0, "OPEN": 0}):
        user_lock = 0.00
    tlist = ''
    balance = 0
    for token in user_balance:
        blnc = user_balance.get(token)
        if token != 'TON':
            try:
                tokenb = float(tcource.get(token)) * float(blnc)
                tlist = tlist + f"*{token}*: {blnc:.2f} ({tokenb:.2f} TON)\n"
                balance += tokenb
            except TypeError:
                tlist = tlist + f"*{token}*: {blnc:.2f}\n"

        else:
            tlist = tlist + f"*{token}*: {blnc:.2f}\n"
            balance += blnc
    isLocked = [True for token in user_balance if
                not isinstance(user_lock.get(token), NoneType) and float(user_lock.get(token)) > 0]
    if len(isLocked) > 0:
        llist = ''
        for token in user_lock:
            if user_lock.get(token) > 0:
                lock = user_lock.get(token)
                if token != 'TON':
                    tokenl = float(tcource.get(token)) * float(lock)
                    llist = llist + f"*{token}*: {lock :.2f} ({tokenl :.2f} TON)\n"
                    balance += tokenl
                else:
                    llist = llist + f"*{token}*: {lock:.2f}\n"
                    balance += user_lock.get(token)
        await call.message.edit_text(text=f'💎 Ваш баланс: \n{tlist}\n⛔ Заблокировано: \n{llist}\n ≈ {balance :.2f} TON',
                                     parse_mode=ParseMode.MARKDOWN, reply_markup=skb.get_backbtn_kb())
    else:
        try:
            await call.message.edit_text(text=f'💎 Ваш баланс: \n{tlist}\n ≈ {balance :.2f} TON',
                                         parse_mode=ParseMode.MARKDOWN, reply_markup=skb.get_backbtn_kb())
        except TelegramBadRequest:
            pass


async def TKsendnum(call: types.CallbackQuery, state: FSMContext):
    id = call.data.replace("TKsendnum:", "")
    deal = dealsdb.get_deal_by_id(id)
    if deal[6] == 'hide' and dealsdb.getdtsbyid(id)[str(deal[8])].get('stage') == '1':
        await state.set_state(MarketStates.TKsendnum)
        await state.update_data(id=id)
        await state.update_data(msg=(call.message.message_id, call.message.chat.id))
        await call.message.edit_text("📲Отправьте ваш номер телефона")
    else:
        await call.message.edit_text('❌ Время истекло', reply_markup=skb.get_backmrktbtn_kb())


async def market(message: Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state:
        await state.set_state(state=None)
        state_data = await state.get_data()
        await state.set_data({'msgid': state_data.get('msgid'), 'chatid': state_data.get('chatid')})
    try:
        await message.edit_text(text="💳 Здесь вы можете\n"
                                     "купить или продать\n"
                                     "OPEN за рубли", reply_markup=get_market_kb())
    except TelegramBadRequest:
        pass


async def offers_process(call: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    _cur_list = data.get("cur_list")
    if isinstance(_cur_list, NoneType):
        _cur_list = 10

    match call.data.replace("_offers", ""):
        case "forward":
            _cur_list = data.get("cur_list") + 10
        case "back":
            _cur_list = data.get("cur_list") - 10
        case "cancel":
            dealstype = data.get('deal_type')
            deals = dealsdb.get_deals_by_type(dealstype)
            text = 'покупки' if dealstype == 'buy' else 'продажи'
            await call.message.edit_text(f'Выберите способ оплаты для {text}', reply_markup=banks_kb(deals, 5))
            return
        case "back_to":
            _cur_list = 10
            typed = 'продать'
            if data.get('deal_type') == 'buy':
                typed = 'купить'
            await call.message.edit_text(f"Здесь вы можете {typed} OPEN за рубли:")
    deals_type = data.get('deal_type')
    bankid = data.get('bankid')
    deals = dealsdb.get_deals_by_type(deals_type)
    active_deals = [deal for deal in deals if deal[6] == '' and deal[11] == config.SUPPORT_BANKS[bankid]]
    sorted_active_deals = sorted(active_deals, key=lambda x: x[7])
    await state.update_data(cur_list=_cur_list)
    await call.message.edit_reply_markup(reply_markup=offers_kb(sorted_active_deals, _cur_list))


async def banks_process(call: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    _cur_list = data.get("cur_list")
    if isinstance(_cur_list, NoneType):
        _cur_list = 5

    match call.data.replace("_banks", ""):
        case "forward":
            _cur_list = _cur_list + 5
        case "back":
            _cur_list = _cur_list - 5
        case "cancel":
            await state.set_state(state=None)
            state_data = await state.get_data()
            await state.set_data({'msgid': state_data.get('msgid'), 'chatid': state_data.get('chatid')})
            return
    dealstype = data.get('deal_type')
    deals = dealsdb.get_deals_by_type(dealstype)
    await state.update_data(cur_list=_cur_list)
    await call.message.edit_reply_markup(reply_markup=banks_kb(deals, _cur_list))


async def offer_process(call: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    id = call.data.replace("offer_id:", "")
    deal = dealsdb.get_deal_by_id(id)
    if deal[6] == '':
        deal_type = deal[2]
        pay_type = deal[11]
        amount = f"{deal[3] :.2f} OPEN"
        allinrub = f"{(float(deal[3]) * float(deal[7])):.2f}₽"
        cource = deal[7]
        min = deal[9]
        minrub = f"{float(deal[9]) * float(deal[7]) :.2f}"
        await call.message.edit_text(f"📢 Объявление #{id}\n\n"
                                     f"🏷️ Цена за один OPEN: {cource}₽\n\n"
                                     f"💵 Доступный обьем: {amount}\n"
                                     f"❗ Лимиты: {min}-{amount}\nили {minrub}-{allinrub}\n\n"
                                     f"🕒 Срок оплаты: 20 мин\n"
                                     f"💳 Способ оплаты: {pay_type}\n\n", reply_markup=skb.get_offer_process_kb(id))


async def mydeals(uid: int, message: Message):
    mydeals = dealsdb.get_deals_by_makerid(uid)
    try:
        await message.edit_text(text="<b>🤝🏼 Все ваши активные обьявления:</b>", reply_markup=get_my_deals_kb(mydeals),
                                parse_mode=ParseMode.HTML)
    except TelegramBadRequest:
        pass


async def myinactivedeals(uid: int, message: Message):
    mydeals = dealsdb.get_deals_by_makerid(uid)
    try:
        await message.edit_text(text="<b>🤝🏼 Все ваши неактивные обьявления:</b>",
                                reply_markup=get_all_unactive_deals_kb(mydeals), parse_mode=ParseMode.HTML)
    except TelegramBadRequest:
        pass


async def allmydeals(uid: int, message: Message):
    mydeals = dealsdb.get_deals_by_listid(dealsdb.get_all_user_deals_id(uid))
    await message.edit_text(text="<b>🤝🏼 Все ваши текущие сделки:</b>\n\nНажмите на сделку что бы перейти к ней",
                            reply_markup=get_my_all_deals_kb(mydeals, uid, True),
                            parse_mode=ParseMode.HTML)


async def dealinfo(call: types.CallbackQuery):
    dealid = call.data.replace('dealinfo:', '')
    deal = dealsdb.get_deal_by_id(dealid)
    await call.message.edit_text(
        text=f"Вся информация: \n\nРаздел: {'Купить 📈' if deal[2] == 'buy' else 'Продать 📉'}\nМинимальная сумма сделки: {deal[9]}\nПлатежное средство: {deal[11]}\nКурс обьявления: {deal[7]} OPEN/₽",
        reply_markup=skb.get_backundealsbtn_kb(),
        parse_mode=ParseMode.HTML)


async def todeal(call: types.CallbackQuery, state: FSMContext):
    uid = str(call.from_user.id)
    dealid = call.data.replace('todeal:', '')
    deal = dealsdb.get_deal_by_id(dealid)
    maker = True if str(deal[1]) == uid else False
    dealtype = deal[2]
    if maker:
        takerid = str(deal[8])

        dts = deal[5].get(takerid)
        if not isinstance(dts.get('launch'), NoneType):
            if not isinstance(dts.get('isSuccess'), NoneType):
                await call.message.edit_text(text='Вы не приняли эту сделку',
                                             reply_markup=skb.get_backmrktbtn_kb())
            if dts.get('stage') == '0':
                await call.message.edit_text(text='Вы отклонили эту сделку',
                                             reply_markup=skb.get_backmrktbtn_kb())

            if dts.get('stage') == '1':
                if dealtype == 'buy':
                    await state.update_data(id=dealid)
                    await call.message.edit_text(
                        "Пользователю нужно отправить номер телефона что бы он перевел вам деньги за OPEN. Нажмите на кнопку с вашим номером",
                        reply_markup=skb.get_buy_offer_accept_kb(deal))
                else:
                    await call.message.edit_text(text="📲Ожидайте когда пользователь отправит номер телефона",
                                                 reply_markup=skb.get_sup_kb())



            if dts.get('stage') == '2':
                if dealtype == 'buy':
                    await call.message.edit_text(text='Ожидайте подтверждения перевода',
                                                 reply_markup=skb.get_sup_kb())

                else:
                    num = deal[4]
                    amrub = float(deal[10]) * float(deal[7])
                    await call.message.edit_text(text=f'📤Вам нужно перевести <code>{amrub :.2f}</code>₽ по {deal[11]} на номер телефона <code>{num}</code> с комментарием <code>Сделка на OpenMarket #{str(deal[0])}</code>. После чего нажать "Подтвердить перевод"',
                                                 reply_markup=skb.get_TKgetnum_kb(dealid),
                                                 parse_mode=ParseMode.HTML)

            if dts.get('stage') == '3':
                if dealtype == 'buy':
                    num = deal[4]
                    amrub = float(deal[10]) * float(deal[7])
                    await call.message.edit_text(text=f'💸 Пользователь подтвердил перевод {amrub :.2f}₽ по {deal[11]} на номер телефона {num} с комментарием "Сделка на OpenMarket #{str(deal[0])}". Проверьте и подтвердите перевод. После подтверждения OPEN-ы перейдут на счет клиента.',
                                                 reply_markup=skb.get_TK_accept_trans_kb(dealid))
                else:
                    await call.message.edit_text(text=f"⏱️ Ожидайте подтверждения сделки покупателем. В случае возникновении проблем пишите в поддержку",
                                                 reply_markup=skb.get_sup_kb())

            if dts.get('stage') == '4':

                await call.message.edit_text(text='Эта сделка прошла успешно',
                                             reply_markup=skb.get_backmrktbtn_kb())

            if isinstance(dts.get('stage'), NoneType):
                if dealtype == 'buy':
                    await call.message.edit_text(f"🚀 Пользователь начал с вами сделку на покупку {deal[10]} OPEN по курсу {deal[7]} RUB/OPEN",
                                           reply_markup=skb.get_acceptMK_kb(dealid))

                else:
                    await call.message.edit_text(f"🚀Пользователь начал с вами сделку на продажу {deal[10]} OPEN по курсу {deal[7]} RUB/OPEN",
                                           reply_markup=skb.get_acceptMK_kb(dealid))



        else:
            await call.message.edit_text(text='Сделка не существует или она уже окночена',
                                         reply_markup=skb.get_backmrktbtn_kb())
    else:
        dts = deal[5].get(uid)
        if not isinstance(dts.get('launch'), NoneType):
            if not isinstance(dts.get('isSuccess'), NoneType):
                await call.message.edit_text(text='Продавец не принял эту сделку',
                                             reply_markup=skb.get_backmrktbtn_kb())

            if dts.get('stage') == '0':
                await call.message.edit_text(text='Продавец отклонили эту сделку',
                                             reply_markup=skb.get_backmrktbtn_kb())

            if dts.get('stage') == '1':
                if deal[2] == 'buy':
                    await call.message.edit_text(
                        text="✅ Продавец принял сделку.📲 Ожидайте номер телефона для покупки OPEN",
                        reply_markup=skb.get_sup_kb())
                else:
                    await call.message.edit_text(text="✅ Продавец принял сделку. Отправьте ему свой телефон",
                                                 reply_markup=skb.get_sell_offer_accept_kb(dealid))

            if dts.get('stage') == '2':
                if dealtype == 'buy':
                    num = deal[4]
                    amrub = float(deal[10]) * float(deal[7])
                    await call.message.edit_text(text=f'💸 Вам нужно перевести <code>{amrub :.2f}</code>₽ по {deal[11]} на номер телефона <code>{num}</code> с комментарием <code>Сделка на OpenMarket #{str(deal[0])}</code>. После чего нажать "Подтвердить перевод"',
                                                 reply_markup=skb.get_sendnum_kb(dealid), parse_mode=ParseMode.HTML)

                else:
                    await call.message.edit_text(text="✅ Номер принят. \n🕓 Ожидайте подтверждение перевода от продавца",
                                                 parse_mode=ParseMode.MARKDOWN,
                                                 reply_markup=skb.get_sup_kb())

            if dts.get('stage') == '3':
                if dealtype == 'buy':
                    await call.message.edit_text(text=f"⏰ Ожидайте подтверждения сделки продавцом. В случае возникновении проблем пишите в поддержку",
                                           reply_markup=skb.get_sup_kb())
                else:
                    num = deal[4]
                    amrub = float(deal[10]) * float(deal[7])
                    await call.message.edit_text(text=f'✅ Продавец подтвердил перевод {amrub:.2f}₽ по {deal[11]} на номер телефона {num} с комментарием "Сделка на OpenMarket #{str(deal[0])}. Проверьте и подтвердите перевод. После подтверждения OPEN-ы перейдут на счет продавца.',
                                           reply_markup=skb.get_MK_accept_trans_kb(dealid))

            if dts.get('stage') == '4':
                await call.message.edit_text(text='Эта сделка прошла успешно',
                                             reply_markup=skb.get_backmrktbtn_kb())

            if isinstance(dts.get('stage'), NoneType):
                if dealtype == 'buy':
                    await call.message.edit_text("🕓 Ожидаем ответа продавца", reply_markup=skb.get_sup_kb())
                else:
                    await call.message.edit_text(
                        "⛔ На момент сделки мы залокировали OPEN на кошелеке\n🕓Ожидаем ответа продавца",
                        reply_markup=skb.get_sup_kb())
        else:
            await call.message.edit_text(text='Сделка не существует или она уже окночена',
                                         reply_markup=skb.get_backmrktbtn_kb())


async def chequemain(call: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    await state.set_state(state=None)
    await state.set_data({'msgid': data.get('msgid'), 'chatid': data.get('chatid')})
    await call.message.edit_text(
        text="В этом разделе вы можете создавать чеки.\n\n"
             "· Персональный чек - для отправки монет одному пользователю\n\n",
        reply_markup=skb.get_cgequesmain_kb())


async def getcheques(call: types.CallbackQuery, args=''):
    cheques = chqdb.get_cheques_by_uid(call.from_user.id)
    activecheques = [cheq for cheq in cheques if cheq[4]]
    await call.message.edit_text(
        text=f"{args}Ваши активные чеки:",
        reply_markup=skb.get_all_cheques(activecheques))


async def cheqinfo(call: types.CallbackQuery):
    cheqid = call.data.replace('cheqinfo:', '')
    cheq = chqdb.get_cheq(cheqid)
    me = await bot.me()
    salt = cheq[5]
    urlcheque = create_deep_link(username=me.username, link_type="start", payload=str(cheqid) + ":" + salt, encode=True)
    await call.message.edit_text(f'Ссылка на активацию чека: \n{urlcheque}\n\nCумма: {cheq[2]} {cheq[3]}',
                                 reply_markup=skb.del_cheq(cheqid))


async def makepcheque(call: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    token = data.get('token')
    amount = data.get('cheqamount')
    salt = getsalt()
    cheqid = chqdb.add_cheq(call.from_user.id, amount, token, salt)
    udb.lock_balance(call.from_user.id, amount, token)
    udb.rem_balance(call.from_user.id, config.CHEQUES_FEE, 'TON')
    me = await bot.me()
    urlcheque = create_deep_link(username=me.username, link_type="start", payload=str(cheqid) + ":" + salt, encode=True)
    await call.message.edit_text(
        text=f"Вы создали чек на сумму {amount} {token}\n"
             f"*На вашем балансе заблокировали эту сумму "
             f"до момента активации чека\n\n"
             f"Вот ссылка:\n{urlcheque}\n",
        reply_markup=skb.get_back_cheque_kb())


async def ActiveDeals(message: Message, state: FSMContext, bankid, n=10):
    await state.set_state(MarketStates.ActiveDeals)
    current_state = await state.get_data()
    deals_type = current_state.get('deal_type')
    deals = dealsdb.get_deals_by_type(deals_type)
    active_deals = []
    for deal in deals:
        if deal[6] == '' and deal[11] == config.SUPPORT_BANKS[bankid]:
            active_deals.append(deal)
    sorted_active_deals = sorted(active_deals, key=lambda x: x[7])
    await state.update_data(bankid=bankid)
    await state.update_data(cur_list=n)
    data = await state.get_data()
    if deals_type == "sell":
        await message.edit_text(text="🔁 Здесь вы можете продать OPEN за рубли.",
                                reply_markup=offers_kb(sorted_active_deals, n))
    else:
        await message.edit_text(text="🔁 Здесь вы можете продать OPEN за рубли.",
                                reply_markup=offers_kb(sorted_active_deals, n))


async def del_deal(call: types.CallbackQuery):
    uid = call.from_user.id
    id = call.data.replace("del:", "")
    amount = dealsdb.get_deal_by_id(id)[3]
    if dealsdb.get_deal_by_id(id)[6] == '':
        udb.relock_balance(uid, amount, "OPEN")
        dealsdb.set_deal_inactive(id)
        await call.message.edit_text("🗑️ Обьявление удалена. Вы можете создать новую.", reply_markup=skb.get_backmrktbtn_kb())
    else:
        await call.message.edit_text("По обьявлению либо сейчас проходит сделка либо оно уже неактивно ",
                                     reply_markup=skb.get_backmrktbtn_kb())


async def pchequetoken(call: types.CallbackQuery):
    await call.message.edit_text(text="Выберите криптовалюту для создания чека",
                                 reply_markup=keyboards.choosekb.get_tokens_kb_for_cheque())


async def pchequeamount(call: types.CallbackQuery, state: FSMContext):
    user_balance = udb.get_balance(call.from_user.id)
    token = call.data.replace('cheque:', '')
    try:
        token_balance = float(user_balance.get('TON') if token == 'TON' else (user_balance.get(token)))
        if token_balance > 0:
            await state.update_data(token=token)
            await call.message.edit_text(
                text=f"Отправьте кол-во криптовалюты для чека: \n\nДоступное кол-во: {token_balance :.2f} {token} \n\nКоммисия за содание чека {config.CHEQUES_FEE} TON",
                reply_markup=skb.get_back_cheque_kb())
            await state.set_state(ChequesStates.getAmount)
            await state.update_data(msg=(call.message.message_id, call.message.chat.id))
        else:
            await call.message.edit_text(text='Недостаточно средств', reply_markup=skb.get_back_cheque_kb())
    except:
        await call.message.edit_text(text='Недостаточно средств', reply_markup=skb.get_back_cheque_kb())


async def calltransfer(uid: int, message: Message, state: FSMContext):
    data = await state.get_data()
    sum = float(data.get('sum'))
    token = data.get('token')
    addr = data.get('addr')
    shardid = udb.get_user_by_uid(uid)[3]
    cource = readcource()
    fee = float(1 if token == 'TON' else cource.get(token))
    if 0 < sum <= float(udb.get_balance(uid).get(token)-(config.WITHDRAW_FEE / fee)):
        if token == 'TON':
            resp = await Wallet.tontransfer(addr, sum, shardid)
        else:
            resp = await Wallet.transfer(addr, sum, token, shardid)
        if resp:
            await message.edit_text(f"💸 Успешно отправлено {sum:.2f} {token}",
                                    reply_markup=skb.get_backbtn_with_sup_kb())
            udb.rem_balance(uid, sum + (config.WITHDRAW_FEE / fee), token)
        else:
            await message.edit_text(
                f"❌ Введен неправильный адрес.\nПереповерьте адрес.\nИ в случае повтора ошибки напишите в техподдержку",
                reply_markup=skb.get_backbtn_with_sup_kb())
    else:
        await message.edit_text("❌ Недостаточно средств. Выберите меньшую сумму.", reply_markup=skb.get_backbtn_kb())


async def withdraw(uid: int, state: FSMContext, call: types.CallbackQuery):
    token = call.data.replace("wd:", "")
    balance = udb.get_balance(uid).get(token)
    if isinstance(balance, NoneType):
        balance = 0
    cource = readcource()
    fee = float(1 if token == 'TON' else cource.get(token))
    if balance < (config.WITHDRAW_FEE / fee):
        await call.message.edit_text(f"💎 Ваш баланс {balance} {token}\n"
                                     f"⚡ Максимум: 0 {token}\n"
                                     f"💰 Комиссия: {(config.WITHDRAW_FEE / fee) :.2f} {token}\n"
                                     f"⛔ Недостаточно средств", reply_markup=skb.get_backbtn_kb())
    else:
        await call.message.edit_text("➡️ Введите сумму для вывода:\n"
                                     f"💎 Ваш баланс: {balance :.2f} {token}\n"
                                     f"⚡ Максимум: {(balance - (config.WITHDRAW_FEE / fee)) // 0.01 / 100} {token}\n"
                                     f"💰 Комиссия: {(config.WITHDRAW_FEE / fee) :.2f} {token}",
                                     reply_markup=skb.get_backbtn_kb())
        await state.update_data(token=token)
        await state.set_state(WithdrawStates.getsum)
        await state.update_data(msg=(call.message.message_id, call.message.chat.id))


async def choosetokenforwd(message):
    try:
        await message.edit_text('🤝 Выберите для вывода любую\n'
                                'поддерживаемую криптовалюту:',
                                reply_markup=keyboards.choosekb.get_tokens_kb_for_dep(False))
    except:
        pass


async def calldep(uid: int, message: Message, call: types.CallbackQuery):
    token = call.data.replace("dep:", "")
    shardid = udb.get_user_by_uid(uid)[3]
    await message.edit_text(f'💲 Чтобы пополнить баланс переведите {token} на адрес:\n\n'
                            f'`{config.SHARDS_ADDRESS[shardid]}`\n\n'
                            f'➕ И добавьте коментарий: `{uid}`\n\n'
                            'Или нажмите на кнопку снизу\n'
                            'и подтвердите перевод в вашем кошельке.',
                            reply_markup=skb.get_calldep_kb(uid, token, shardid),
                            parse_mode=ParseMode.MARKDOWN)


async def choosetokenfordep(message: Message):
    await message.edit_text('🤝 Выберите для пополнения любую\n'
                            'поддерживаемую криптовалюту:', reply_markup=keyboards.choosekb.get_tokens_kb_for_dep(True))


async def market_makedeal(message: Message, state: FSMContext):
    await state.update_data(maker=True)
    await state.set_state(MarketStates.BuyorSell)
    await message.edit_text("⚖️ Выберите тип сделки:", reply_markup=skb.get_market_makedeal_kb())


async def market_CorB(uid: int, message: Message, state: FSMContext, data: str):
    state_data = await state.get_data()
    if state_data.get('maker'):
        deals = dealsdb.get_deals_by_makerid(uid)
        doit = True
        for deal in deals:
            if deal[2] == data and deal[6] == '':
                doit = False
        if doit:
            await state.update_data(deal_type=data)
            deals = dealsdb.get_deals_by_type(data)
            text = 'покупки' if data == 'buy' else 'продажи'
            await message.edit_text(f'Выберите способ оплаты для {text}', reply_markup=banks_kb(deals, 5))

        else:
            await message.edit_text(
                "🙅‍♂️ У вас уже создано обьявление в этом разделе. Вы можете удалить его в разделе мои сделки.",
                reply_markup=skb.get_backmrktbtn_kb())

    else:
        await state.update_data(deal_type=data)
        deals = dealsdb.get_deals_by_type(data)
        text = 'покупки' if data == 'buy' else 'продажи'
        await message.edit_text(f'Выберите способ оплаты для {text}', reply_markup=banks_kb(deals, 5))


async def MK_give_num(message: Message, state: FSMContext, bankid):
    data = await state.get_data()
    dealtype = data.get('deal_type')
    text = 'получить' if dealtype == 'buy' else 'отправлять'
    await message.edit_text("Отправьте номер привязаный\n"
                            f"к вашему банку по {config.SUPPORT_BANKS[bankid]}.\n"
                            "И на который вы планируете\n"
                            f"{text} рубли за OPEN.\n\n"
                            "Например: 79123456789",
                            reply_markup=skb.get_backmrktbtn_kb())
    await state.update_data(bankid=bankid)
    await state.update_data(msg=(message.message_id, message.chat.id))
    await state.set_state(MarketStates.PaymentsNum)


async def deal_start(call: types.CallbackQuery, state: FSMContext):
    await state.set_state(MarketStates.chooseAmount)
    id = call.data.replace("startdeal:", "")
    deal = dealsdb.get_deal_by_id(id)
    min = deal[9]
    max = deal[3]
    await state.update_data(id=id)
    deal_type = (await state.get_data()).get('deal_type')
    typ = 'купить'
    if deal_type == "sell":
        typ = 'продать'
    msg = await call.message.edit_text("Отправьте кол-во OPEN которое вы хотите " + typ + f"\nОт {min} до {max} OPEN",
                                       reply_markup=skb.get_backmrktbtn_kb())
    await state.update_data(del_msg=(call.message.message_id, call.message.chat.id))


async def MK_accept_trans(call: types.CallbackQuery):
    id = call.data.replace("MK_accept_trans:", "")
    deal = dealsdb.get_deal_by_id(id)
    num = deal[4]
    amrub = float(deal[10]) * float(deal[7])
    await call.message.delete()
    takerid = deal[8]
    if deal[6] == 'hide' and deal[5].get(str(takerid)).get('stage') == '2':
        dealsdb.set_to_dts_stage(id, deal[8], 3)
        await bot.send_message(chat_id=deal[1],
                               text=f"⏱️ Ожидайте подтверждения сделки покупателем. В случае возникновении проблем пишите в поддержку",
                               reply_markup=skb.get_sup_kb())

        await bot.send_message(chat_id=deal[8],
                               text=f'✅ Продавец подтвердил перевод {amrub :.2f}₽ по {deal[11]} на номер телефона {num} с комментарием "Сделка на OpenMarket #{str(deal[0])}. Проверьте и подтвердите перевод. После подтверждения OPEN-ы перейдут на счет продавца.',
                               reply_markup=skb.get_MK_accept_trans_kb(id))
    else:
        await call.message.answer(text='Сделка уже не актуальна', reply_markup=skb.get_backmrktbtn_kb())
    await call.message.delete()


async def TK_accept_deal(call: types.CallbackQuery):
    id = call.data.replace("TK_accept_deal:", "")
    deal = dealsdb.get_deal_by_id(id)
    makerid = deal[1]
    takerid = deal[8]
    amount = deal[10]
    amrub = (float(deal[10]) * float(deal[7]))
    if deal[6] == 'hide' and deal[5].get(str(takerid)).get('stage') == '3':
        udb.from_blnclock_to_anuser(float(amount), takerid, makerid, "OPEN")
        dealsdb.set_to_dts_stage(id, deal[8], 4)
        dealsdb.set_deal_active(id)
        dealsdb.set_to_dts_time_end(id, datetime.now(), deal[8])
        await bot.send_message(chat_id=makerid, text=f"✅ Сделка прошла успешно.\n+{amount} OPEN\n-{amrub :.2f}₽",
                               reply_markup=skb.get_backmrktbtn_kb())
        await bot.send_message(chat_id=takerid, text=f"✅ Сделка прошла успешно.\n-{amount} OPEN\n+{amrub :.2f}₽",
                               reply_markup=skb.get_backmrktbtn_kb())
        dealsdb.rem_amount_by_id(id, amount)

        deal = dealsdb.get_deal_by_id(id)
        if float(deal[3]) < float(deal[9]):
            dealsdb.set_deal_inactive(id)
            await bot.send_message(chat_id=makerid, text=f"🏁 Обьявление исчерпано.Вы можете создать новое.",
                                   reply_markup=skb.get_backmrktbtn_kb())
    else:
        await call.message.answer(text='Сделка уже не актуальна', reply_markup=skb.get_backmrktbtn_kb())

    await call.message.delete()


async def MK_accept_deal(call: types.CallbackQuery):
    id = call.data.replace("MK_accept_deal:", "")
    deal = dealsdb.get_deal_by_id(id)
    makerid = deal[1]
    takerid = deal[8]
    amount = deal[10]
    amrub = (float(deal[10]) * float(deal[7]))
    if deal[6] == 'hide' and deal[5].get(str(takerid)).get('stage') == '3':
        udb.from_blnclock_to_anuser(amount, makerid, takerid, "OPEN")
        dealsdb.set_deal_active(id)
        dealsdb.set_to_dts_stage(id, deal[8], 4)
        dealsdb.set_to_dts_time_end(id, datetime.now(), deal[8])
        await bot.send_message(chat_id=makerid, text=f"✅ Сделка прошла успешно.\n-{amount} OPEN\n+{amrub :.2f}₽")
        await bot.send_message(chat_id=takerid, text=f"✅ Сделка прошла успешно.\n+{amount} OPEN\n-{amrub :.2f}₽")
        dealsdb.rem_amount_by_id(id, amount)

        deal = dealsdb.get_deal_by_id(id)
        if float(deal[3]) < float(deal[9]):
            dealsdb.set_deal_inactive(id)
            udb.relock_balance(makerid, float(deal[3]), "OPEN")
            udb.clearlock_by_id(makerid, "OPEN")
            await bot.send_message(chat_id=makerid,
                                   text=f"🏁 Обьявление исчерпано.Средства возвращены на баланс\n+{deal[3]} OPEN",
                                   reply_markup=skb.get_backmrktbtn_kb())
    else:
        await call.message.answer(text='Сделка уже не актуальна', reply_markup=skb.get_backmrktbtn_kb())
    try:
        await call.message.delete()
    except:
        pass


async def sendnum(state: FSMContext, call: types.CallbackQuery):
    data = await state.get_data()
    id = data.get('id')
    deal = dealsdb.get_deal_by_id(id)
    if deal[6] == 'hide' and dealsdb.getdtsbyid(id)[str(deal[8])].get('stage') == '1':
        num = deal[4]
        amrub = float(deal[10]) * float(deal[7])
        dealsdb.set_to_dts_stage(id, deal[8], 2)
        dealsdb.set_to_dts_time_end(id, datetime.now(), deal[8])
        await call.message.edit_text(text='Ожидайте подтверждения перевода', reply_markup=skb.get_sup_kb())
        await bot.send_message(chat_id=deal[8],
                               text=f'💸 Вам нужно перевести <code>{amrub :.2f}</code>₽ по {deal[11]} на номер телефона <code>{num}</code> с комментарием <code>Сделка на OpenMarket #{str(deal[0])}</code>. После чего нажать "Подтвердить перевод"',
                               reply_markup=skb.get_sendnum_kb(id), parse_mode=ParseMode.HTML)
    else:
        await call.message.edit_text('❌ Время истекло', reply_markup=skb.get_backmrktbtn_kb())


async def TK_accept_trans(call: types.CallbackQuery):
    id = call.data.replace("TK_accept_trans:", "")
    deal = dealsdb.get_deal_by_id(id)
    num = deal[4]
    takerid = deal[8]
    amrub = float(deal[10]) * float(deal[7])

    if deal[6] == 'hide' and deal[5].get(str(takerid)).get('stage') == '2':
        dealsdb.set_to_dts_stage(id, deal[8], 3)
        await bot.send_message(chat_id=deal[8],
                               text=f"⏰ Ожидайте подтверждения сделки продавцом. В случае возникновении проблем пишите в поддержку",
                               reply_markup=skb.get_sup_kb())
        await bot.send_message(chat_id=deal[1],
                               text=f'💸 Пользователь подтвердил перевод {amrub :.2f}₽ по {deal[11]} на номер телефона {num} с комментарием "Сделка на OpenMarket #{str(deal[0])}". Проверьте и подтвердите перевод. После подтверждения OPEN-ы перейдут на счет клиента.',
                               reply_markup=skb.get_TK_accept_trans_kb(id))
    else:
        await call.message.answer(text='Сделка уже не актуальна', reply_markup=skb.get_backmrktbtn_kb())
    await call.message.delete()


async def offer_accept(call: types.CallbackQuery, state: FSMContext):
    id = call.data.replace("accept:", "")
    deal = dealsdb.get_deal_by_id(id)
    if deal[6] == 'hide' and not dealsdb.getdtsbyid(id)[str(deal[8])].get('stage') == '1' and not dealsdb.getdtsbyid(id)[str(deal[8])].get('stage') == '2' and not dealsdb.getdtsbyid(id)[str(deal[8])].get('stage') == '3':
        dealsdb.set_to_dts_stage(id, deal[8], 1)
        dealsdb.set_to_dts_timestart(deal[0], datetime.now(), deal[8])
        if deal[2] == 'buy':
            await state.update_data(id=id)
            await call.message.edit_text(
                "Пользователю нужно отправить номер телефона что бы он перевел вам деньги за OPEN. Нажмите на кнопку с вашим номером",
                reply_markup=skb.get_buy_offer_accept_kb(deal))
            await bot.send_message(chat_id=deal[8],
                                   text="✅ Продавец принял сделку.📲 Ожидайте номер телефона для покупки OPEN")
        else:
            await call.message.edit_text(text="📲Ожидайте когда пользователь отправит номер телефона",
                                         reply_markup=skb.get_sup_kb())
            await bot.send_message(chat_id=deal[8], text="✅ Продавец принял сделку. ",
                                   reply_markup=skb.get_sell_offer_accept_kb(id))
    else:
        await call.message.edit_text('❌ Время истекло', reply_markup=skb.get_backmrktbtn_kb())


async def deal_decline(call: types.CallbackQuery, state: FSMContext):
    id = call.data.replace("decline:", "")
    deal = dealsdb.get_deal_by_id(id)
    if deal[6] == 'hide' and not dealsdb.getdtsbyid(id)[str(deal[8])].get('stage') == '1' and not dealsdb.getdtsbyid(id)[str(deal[8])].get('stage') == '2' and not dealsdb.getdtsbyid(id)[str(deal[8])].get('stage') == '3':
        dealsdb.set_deal_active(id)
        await market(call.message, state)
        if deal[2] == 'sell':
            await bot.send_message(chat_id=deal[8], text="❌ Продавец отклонил сделку. Средства возвращены на баланс.")
        else:
            await bot.send_message(chat_id=deal[8], text="❌ Продавец отклонил сделку.")
        dealsdb.set_to_dts_stage(id, deal[8], 0)
        dealsdb.set_to_dts_time_end(id, datetime.now(), deal[8])
        udb.relock_balance(deal[8], float(deal[10]), "OPEN")
    else:
        await call.message.edit_text('❌ Время истекло', reply_markup=skb.get_backmrktbtn_kb())


async def dealpayed(call: types.CallbackQuery, state: FSMContext):
    state_data = await state.get_data()
    msg = state_data.get('msg')
    uid = state_data.get('uid')
    tonbalance = udb.get_balance(uid).get('TON')
    dealispayed = tonbalance >= config.MARKET_DEAL_PRICE
    bankid = state_data.get('bankid')
    amount = state_data.get('amount')
    if dealispayed:
        udb.rem_balance(uid, config.MARKET_DEAL_PRICE, "TON")
        if state_data.get('deal_type') == "buy":
            deal_type = state_data.get('deal_type')
            number = state_data.get('number')
            cource = state_data.get('cource')
            min = state_data.get('min')
            dt = datetime.now()
            udb.lock_balance(uid, amount, "OPEN")
            dealsdb.add_deal(uid, amount, deal_type, number, dt, cource, min, config.SUPPORT_BANKS[bankid])
            await bot.edit_message_text(text="➕ Сделка добавлена.\n"
                                             "🔔 Вы получите уведомление когда кто-либо подтвердит сделку.\n"
                                             "⛔ Средства для безопасности сделки заблокированы.\n"
                                             "🔄 В случае отмены сделки все средства будут возвращены",
                                        reply_markup=skb.get_backmrktbtn_kb(), chat_id=msg[1], message_id=msg[0])
            await state.set_state(state=None)
            state_data = await state.get_data()
            await state.set_data({'msgid': state_data.get('msgid'), 'chatid': state_data.get('chatid')})
        elif state_data.get('deal_type') == "sell":
            deal_type = state_data.get('deal_type')
            number = state_data.get('number')
            cource = state_data.get('cource')
            dt = datetime.now()
            min = state_data.get('min')
            dealsdb.add_deal(uid, amount, deal_type, number, dt, cource, min, config.SUPPORT_BANKS[bankid])
            await bot.edit_message_text(text="➕ Сделка добавлена.\n"
                                             "🔔 Вы получите уведомление\n"
                                             "когда кто-либо подтвердит сделку.\n",
                                        reply_markup=skb.get_backmrktbtn_kb(), chat_id=msg[1], message_id=msg[0])
            await state.set_state(state=None)
            state_data = await state.get_data()
            await state.set_data({'msgid': state_data.get('msgid'), 'chatid': state_data.get('chatid')})
    else:
        await bot.edit_message_text(text='Недостаточно средств. Пополните баланс.', reply_markup=skb.get_backbtn_kb(),
                                    chat_id=msg[1], message_id=msg[0])


async def cheqdel(call):
    cheqid = int(call.data.replace('delcheq:', ''))
    cheq = chqdb.get_cheq(cheqid)
    if not isinstance(cheq, NoneType):
        if cheq[4]:
            chqdb.set_cheq_inactive(cheqid)
            udb.relock_balance(cheq[1], cheq[2], str(cheq[3]))
            await getcheques(call, '✅ Чек удален, средства возвращены на баланс\n\n')
        else:
            await getcheques(call, '⛔ Чек неактивен\n\n')
    else:
        await getcheques(call, '⛔ Чек не найден\n\n')
