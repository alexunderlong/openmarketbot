from aiogram import types
from aiogram.enums import ParseMode
from aiogram.exceptions import TelegramBadRequest
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from bot import config
from dbs import udb, dealsdb
from keyboards.marketkb import get_market_kb
from keyboards.mydealskb import get_my_deals_kb
from keyboards.offerskb import offers_kb
import keyboards.smallkbs as skb
from utils.settings import bot
from utils import Wallet
from utils.settings import MarketStates, WithdrawStates
from aiogram.methods.edit_message_text import EditMessageText

async def callbalance(uid, call):
    user_balance = float(udb.get_balance(uid)[0])
    user_lock = udb.get_lock(uid)[0]
    if user_lock == '':
        user_lock = 0.00
    if float(user_lock) > 0:
        await call.message.edit_text(text=f'💎Ваш баланс: {user_balance:.2f} OPEN\n⛔Заблокировано: {user_lock:.2f} OPEN',
                             parse_mode=ParseMode.MARKDOWN, reply_markup=skb.get_backbtn_kb())
    else:
        try:
            await call.message.edit_text(text=f'💎Ваш баланс: {user_balance:.2f} OPEN',
                                parse_mode=ParseMode.MARKDOWN, reply_markup=skb.get_backbtn_kb())
        except TelegramBadRequest:
            pass

async def TKsendnum(call: types.CallbackQuery, state: FSMContext):
    id = call.data.replace("TKsendnum:", "")
    await state.set_state(MarketStates.TKsendnum)
    await state.update_data(id=id)
    await state.update_data(msg=call.message)
    await call.message.edit_text("📲Отправьте ваш номер телефона")

async def market(message: Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state:
        await state.clear()
    try:
        await message.edit_text(text="💳Здесь вы можете\n"
                                "купить или продать\n"
                                "OPEN за рубли", reply_markup=get_market_kb())
    except TelegramBadRequest:
        pass

async def offers_process(call: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    _cur_list = 0

    match call.data.replace("_offers", ""):
        case "forward":
            _cur_list = data.get("cur_list") + 10
        case "back":
            _cur_list = data.get("cur_list") - 10
        case "cancel":
            await state.clear()
            await call.message.delete()
            return
    deals_type = data.get('deal_type')
    deals = dealsdb.get_deals_by_type(deals_type)
    active_deals = []
    for deal in deals:
        if deal[6] == '':
            active_deals.append(deal)
    sorted_active_deals = sorted(active_deals, key=lambda x: x[7])

    await state.update_data(cur_list=_cur_list)
    await call.message.edit_reply_markup(reply_markup=offers_kb(sorted_active_deals, _cur_list))

async def offer_process(call: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    id = call.data.replace("offer_id:", "")
    deal = dealsdb.get_deal_by_id(id)
    if deal[6] == '':
        deal_type = deal[2]
        pay_type = "СБП"
        amount = f"{deal[3]:.2f} OPEN"
        allinrub = f"{float(deal[3]) * float(deal[7]):.2f}₽"
        cource = deal[7]
        min = deal[9]
        minrub = f"{float(deal[9]) * float(deal[7]):.2f}"
        await call.message.edit_text(f"📢Объявление #{id}\n\n"
                              f"🏷️Цена за один OPEN: {cource}₽\n\n"
                              f"💵Доступный обьем: {amount}\n"
                              f"❗Лимиты: {min}-{amount}\nили {minrub}-{allinrub}\n\n"
                              f"🕒Срок оплаты: 20 мин\n"
                              f"💳Способ оплаты: {pay_type}\n\n", reply_markup=skb.get_offer_process_kb(id))

async def mydeals(uid: int, message: Message):
    mydeals = dealsdb.get_deals_by_makerid(uid)
    try:
        await message.edit_text(text="<b>🤝🏼Ваши сделки:</b>\n☝У вас может быть только одна сделка в разделе Купить и одна в разделе Продать. ✋Но вы всегда можете закрыть обьявления здесь, просто нажав на кнопку обьявления", reply_markup=get_my_deals_kb(mydeals), parse_mode=ParseMode.HTML)
    except TelegramBadRequest:
        pass
async def ActiveDeals(message: Message, state: FSMContext, n = 10):
    await state.set_state(MarketStates.ActiveDeals)
    current_state = await state.get_data()
    deals_type = current_state.get('deal_type')
    deals = dealsdb.get_deals_by_type(deals_type)
    active_deals = []
    for deal in deals:
        if deal[6] == '':
            active_deals.append(deal)
    sorted_active_deals = sorted(active_deals, key=lambda x:x[7])
    await state.update_data(cur_list=n)
    data = await state.get_data()
    if deals_type == "sell":
        await message.edit_text(text="🔁Здесь вы можете продать OPEN за рубли.", reply_markup=offers_kb(sorted_active_deals, n))
    else:
        await message.edit_text(text="🔁Здесь вы можете продать OPEN за рубли.", reply_markup=offers_kb(sorted_active_deals, n))

async def del_deal(call: types.CallbackQuery):
    uid = call.from_user.id
    id = call.data.replace("del:", "")
    amount = dealsdb.get_deal_by_id(id)[3]
    udb.relock_balance(uid, amount/(1-config.MARKET_MAKER_FEE))
    dealsdb.set_deal_hide(id)
    await call.message.edit_text("🗑️Сделка удалена. Вы можете создать новую.", reply_markup=skb.get_backmrktbtn_kb())

async def calltransfer(uid: int, message: Message, state: FSMContext):
    sum = float((await state.get_data()).get('sum'))
    addr = (await state.get_data()).get('addr')
    if (udb.get_balance(uid)[0] >= sum + config.WITHDRAW_FEE):
        resp = await Wallet.transfer(addr, sum)
        if resp:
            await message.edit_text(f"💸Успешно отправлено {sum} OPEN", reply_markup=skb.get_backbtn_kb())
            udb.rem_balance(uid, sum + config.WITHDRAW_FEE)
        else:
            await message.edit_text(f"❌Введен неправильный адрес.\nПереповерьте адрес.\nИ в случае повтора ошибки напишите {config.SUPPORT_USERNAME}", reply_markup=skb.get_backbtn_kb())
    else:
        await message.edit_text("❌Недостаточно средств. Отправьте меньшую сумму.", reply_markup=skb.get_backbtn_kb())
async def withdraw(uid: int, message: Message, state: FSMContext):

    balance = udb.get_balance(uid)[0]
    if balance < (config.MIN_WITHDRAW + config.WITHDRAW_FEE):
        await message.edit_text(f"💎Ваш баланс {balance} OPEN\n"
                                "⚡Максимум: 0 OPEN\n"
                                f"🆙Минимальный вывод: {config.MIN_WITHDRAW} OPEN\n"
                                f"💰Комиссия: {config.WITHDRAW_FEE} OPEN\n"
                                f"⛔Вывод не доступен", reply_markup=skb.get_backbtn_kb())
    else:
        await message.edit_text("➡️Введите сумму для вывода:\n"
                             f"💎Ваш баланс: {balance} OPEN\n"
                             f"⚡Максимум: {balance - config.WITHDRAW_FEE} OPEN\n"
                             f"🆙Минимальный вывод: {config.MIN_WITHDRAW} OPEN\n"
                             f"💰Комиссия: {config.WITHDRAW_FEE} OPEN", reply_markup=skb.get_backbtn_kb())
        await state.set_state(WithdrawStates.getsum)
        await state.update_data(msg=message)


async def calldep(uid: int, message: Message):
    await message.edit_text(f'💲Чтобы пополнить баланс переведите OPEN на адрес:\n\n'
                            f'`{config.DEPOSIT_ADDRESS}`\n\n'
                            f'➕И добавьте коментарий: `{uid}`\n\n'
                            'Или нажмите на кнопку снизу\n'
                            'и подтвердите перевод в вашем кошельке.',
                         reply_markup=skb.get_calldep_kb(uid),
                         parse_mode=ParseMode.MARKDOWN)

async def market_makedeal(message: Message, state: FSMContext):
    await state.set_data({'maker': True})
    await state.set_state(MarketStates.BuyorSell)
    await message.edit_text("⚖️Выберите тип сделки:", reply_markup=skb.get_market_makedeal_kb())


async def market_CorB(uid: int, message: Message, state: FSMContext, data: str):
    state_data = await state.get_data()
    if state_data.get('maker'):
        deals = dealsdb.get_deals_by_makerid(uid)
        doit = True
        for deal in deals:
            if deal[2] == data and deal[6] == '':
                doit = False
        if doit:
            await state.set_data({'maker': state_data.get('maker'), 'deal_type': data})
            await state.set_state(MarketStates.PaymentsNum)
            if data == 'sell':
                await message.edit_text("На текущий момент доступны сделки\n"
                                     "только с оплатой в СБП.\n"
                                     "Отправьте номер привязаный\n"
                                     "к вашему банку по СБП.\n"
                                     "С которой вы планируете отправлять"
                                     "рубли за токен OPEN.\n\n"
                                     "Например: 79123456789", reply_markup=skb.get_backmrktbtn_kb())
            else:
                await message.edit_text("На текущий момент доступны сделки\n"
                                     "только с оплатой в СБП.\n"
                                     "Отправьте номер привязаный\n"
                                     "к вашему банку по СБП.\n"
                                     "И на который вы планируете\n"
                                     "получить рубли за OPEN.\n\n"
                                     "Например: 79123456789", reply_markup=skb.get_backmrktbtn_kb())
            await state.update_data(msg=message)

        else:
            await message.edit_text(
                "🙅‍♂️У вас уже создано обьявление в этом разделе. Вы можете удалить его в разделе мои сделки.", reply_markup=skb.get_backmrktbtn_kb())

    else:
        await state.set_data({'deal_type': data})

        await message.edit_text("❗На текущий момент доступны сделки "
                             "только с оплатой в СБП.", reply_markup=skb.get_TK_marketCorB_kb())


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
    await call.message.edit_text("Отправьте кол-во OPEN которое вы хотите " + typ + f"\nОт {min} до {max} OPEN", reply_markup=skb.get_backmrktbtn_kb())

async def MK_accept_trans(call: types.CallbackQuery):

    id = call.data.replace("MK_accept_trans:", "")
    deal = dealsdb.get_deal_by_id(id)
    num = deal[4]
    amrub = float(deal[10]) * float(deal[7])
    await call.message.delete()
    await bot.send_message(chat_id=deal[1], text=f"⏱️Ожидайте подтверждения сделки покупателем. В случае возникновении проблем пишите: {config.SUPPORT_USERNAME}")

    await bot.send_message(chat_id=deal[8],
                           text=f'✅Продавец подтвердил перевод {amrub:.2f}₽ по СБП на номер телефона {num} с комментарием "Сделка на OpenMarket #{id}{str(deal[8])}". Проверьте и подтвердите перевод. После подтверждения OPEN-ы перейдут на счет продавца.', reply_markup=skb.get_MK_accept_trans_kb(id))

async def TK_accept_deal(call: types.CallbackQuery):
    id = call.data.replace("TK_accept_deal:", "")
    deal = dealsdb.get_deal_by_id(id)
    makerid = deal[1]
    takerid = deal[8]
    amount = deal[10]
    amrub = (float(deal[10]) * float(deal[7]))
    await call.message.delete()
    udb.from_bknclock_to_anuser(float(amount)*float(1 - config.MARKET_MAKER_FEE), takerid, makerid)
    await bot.send_message(chat_id=makerid, text=f"✅Сделка прошла успешно.\n+{amount} OPEN\n-{amrub:.2f}₽")
    await bot.send_message(chat_id=takerid, text=f"✅Сделка прошла успешно.\n-{amount} OPEN\n+{amrub:.2f}₽")
    dealsdb.rem_amount_by_id(id, amount)
    dealsdb.set_deal_active(id)
    deal = dealsdb.get_deal_by_id(id)
    if float(deal[3]) < float(deal[9]):
        dealsdb.set_deal_hide(id)
        await bot.send_message(chat_id=makerid, text=f"🏁Обьявление исчерпано.Вы можете создать новое.", reply_markup=skb.get_backmrktbtn_kb())

async def MK_accept_deal(call: types.CallbackQuery):
    id = call.data.replace("MK_accept_deal:", "")
    deal = dealsdb.get_deal_by_id(id)
    makerid = deal[1]
    takerid = deal[8]
    amount = deal[10]
    amrub = (float(deal[10]) * float(deal[7]))
    await call.message.delete()
    udb.from_bknclock_to_anuser(amount, makerid, takerid)
    await bot.send_message(chat_id=makerid, text=f"✅Сделка прошла успешно.\n-{amount} OPEN\n+{amrub:.2f}₽")
    await bot.send_message(chat_id=takerid, text=f"✅Сделка прошла успешно.\n+{amount} OPEN\n+{amrub:.2f}₽")
    dealsdb.rem_amount_by_id(id, amount)
    dealsdb.set_deal_active(id)
    deal = dealsdb.get_deal_by_id(id)
    if float(deal[3]) < float(deal[9]):
        dealsdb.set_deal_hide(id)
        udb.relock_balance(makerid, float(deal[3]))
        udb.clearlock_by_id(makerid)
        await bot.send_message(chat_id=makerid, text=f"🏁Обьявление исчерпано.Средства возвращены на баланс\n+{deal[3]} OPEN", reply_markup=skb.get_backmrktbtn_kb())

async def sendnum(state: FSMContext, call: types.CallbackQuery):
    data = await state.get_data()
    id = data.get('id')
    deal = dealsdb.get_deal_by_id(id)
    num = deal[4]
    amrub = float(deal[10])*float(deal[7])

    await call.message.delete()
    await bot.send_message(chat_id=deal[8], text=f'💸Вам нужно перевести <code>{amrub}</code>₽ по СБП на номер телефона <code>{num}</code> с комментарием <code>Сделка на OpenMarket #{id}{str(deal[8])}</code>. После чего нажать "Подтвердить перевод"', reply_markup=skb.get_sendnum_kb(id), parse_mode=ParseMode.HTML)

async def TK_accept_trans(call: types.CallbackQuery):
    id = call.data.replace("TK_accept_trans:", "")
    deal = dealsdb.get_deal_by_id(id)
    num = deal[4]
    amrub = float(deal[10]) * float(deal[7])
    await call.message.delete()
    await bot.send_message(chat_id=deal[8], text=f"⏰Ожидайте подтверждения сделки продавцом. В случае возникновении проблем пишите: {config.SUPPORT_USERNAME}")
    await bot.send_message(chat_id=deal[1],
                           text=f'💸Пользователь подтвердил перевод {amrub}₽ по СБП на номер телефона {num} с комментарием "Сделка на OpenMarket #{id}{str(deal[8])}". Проверьте и подтвердите перевод. После подтверждения OPEN-ы перейдут на счет клиента.', reply_markup=skb.get_TK_accept_trans_kb(id))



async def offer_accept(call: types.CallbackQuery, state: FSMContext):
    id = call.data.replace("accept:", "")
    deal = dealsdb.get_deal_by_id(id)
    if deal[2] == 'buy':

        await state.set_data({'id': id})
        await call.message.edit_text("Пользователю нужно отправить номер телефона что бы он перевел вам деньги за OPEN. Нажмите на кнопку с вашим номером", reply_markup=skb.get_buy_offer_accept_kb(deal))
        await bot.send_message(chat_id=deal[8], text="Продавец принял сделку. Ожидайте номер телефона для покупки OPEN")
    else:
        await call.message.edit_text(text="📲Ожидайте когда пользователь отправит номер телефона")
        await bot.send_message(chat_id=deal[8], text="✅Продавец принял сделку. ", reply_markup=skb.get_sell_offer_accept_kb(id))



async def deal_decline(call: types.CallbackQuery, state: FSMContext):
    id = call.data.replace("decline:", "")
    deal = dealsdb.get_deal_by_id(id)
    dealsdb.set_deal_active(id)
    await call.message.delete()
    await bot.send_message(chat_id=deal[8], text="❌Продавец отклонил сделку. Средства возвращены на баланс.")
    print(udb.relock_balance(deal[8], float(deal[10])))

