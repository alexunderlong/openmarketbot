from aiogram import Router
from aiogram.enums import ParseMode
from aiogram.exceptions import TelegramBadRequest
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
import re
import keyboards.smallkbs as skb

from bot import config
from dbs import dealsdb, udb
import datetime
from utils.settings import MarketStates, bot

router = Router()


@router.message(MarketStates.TKsendnum)
async def TKgetnum(message: Message, state: FSMContext):
    data = await state.get_data()

    try:
        await message.delete()
        w = data.get('errmsg')
        await w.delete()
    except TelegramBadRequest:
        pass
    except AttributeError:
        pass
    txt = str(message.text)
    result = re.match(r'^(\+7|7|8)?[\s\-]?\(?[489][0-9]{2}\)?[\s\-]?[0-9]{3}[\s\-]?[0-9]{2}[\s\-]?[0-9]{2}$', txt)
    if(bool(result)):
        id = data.get('id')
        msg = data.get('msg')
        dealsdb.set_takernum_by_id(id, txt)
        deal = dealsdb.get_deal_by_id(id)
        num = deal[4]
        amrub = float(deal[10]) * float(deal[7])
        await msg.edit_text("✅ Номер принят. \n🕓 Ожидайте подтверждение перевода от продавца", parse_mode=ParseMode.MARKDOWN)
        await bot.send_message(chat_id=deal[1],
                               text=f'📤Вам нужно перевести <code>{amrub}</code>₽ по СБП на номер телефона <code>{num}</code> с комментарием <code>Сделка на OpenMarket #{id}{str(deal[8])}</code>. После чего нажать "Подтвердить перевод"',
                               reply_markup=skb.get_TKgetnum_kb(id),
                               parse_mode=ParseMode.HTML)
    else:
        w = await message.answer("❌ Неправильный номер номер телефона. Попробуйте еще.")
        await state.update_data(errmsg=w)



@router.message(MarketStates.chooseAmount)
async def chooseAmount(message: Message, state: FSMContext):
    try:
        await message.delete()
        ermsg = (await state.get_data()).get('ermsg')
        await ermsg.delete()
    except TelegramBadRequest:
        pass
    except AttributeError:
        pass
    try:
        buyamount = float(message.text)
        uid = message.from_user.id
        data = await state.get_data()
        id = data.get('id')
        deal = dealsdb.get_deal_by_id(id)
        min = float(deal[9])
        max = float(deal[3])
        makerid = deal[1]
        if min <= buyamount <= max:
            if makerid != uid:
                if data.get('deal_type') == 'sell' and float(buyamount) > float(udb.get_balance(uid)[0]):
                        await message.answer("❌ Недостаточно средств")
                else:

                    dealsdb.set_takerid_by_id(id, uid)
                    dealsdb.set_deal_hide(id)
                    dealsdb.set_takeramount_by_id(id, buyamount)

                    if data.get('deal_type') == 'sell':
                        await message.answer("⛔ На момент сделки мы залокировали OPEN на кошелеке\n🕓Ожидаем ответа продавца")
                        udb.lock_balance(uid, buyamount)
                        await bot.send_message(makerid, f"🚀Пользователь начал с вами сделку на продажу {buyamount} OPEN по курсу {deal[7]} RUB/OPEN", reply_markup=skb.get_acceptMK_kb(id))
                    else:
                        await message.answer("🕓 Ожидаем ответа продавца")
                        await bot.send_message(makerid, f"🚀 Пользователь начал с вами сделку на покупку {buyamount} OPEN по курсу {deal[7]} RUB/OPEN", reply_markup=skb.get_acceptMK_kb(id))
            else:
                w = await message.answer("❌ Вы не можете начать сделку с самим собой.", reply_markup=skb.get_backmrktbtn_kb())
                await state.update_data(ermsg=w)
        else:
            w = await message.answer("❌ Не соблюдены условия сделки", reply_markup=skb.get_backmrktbtn_kb())
            await state.update_data(ermsg=w)
    except ValueError:
        w = await message.answer("❌ Некорректная сумма", reply_markup=skb.get_backmrktbtn_kb())
        await state.update_data(ermsg=w)





@router.message(MarketStates.PaymentsNum)
async def getmarketnum(message: Message, state: FSMContext):
    try:
        await message.delete()
        ermsg = (await state.get_data()).get('ermsg')
        await ermsg.delete()
    except Exception:
        pass
    try:
        txt = str(message.text)
        result = re.match(r'^(\+7|7|8)?[\s\-]?\(?[489][0-9]{2}\)?[\s\-]?[0-9]{3}[\s\-]?[0-9]{2}[\s\-]?[0-9]{2}$', txt)

        if bool(result):
            state_data = await state.get_data()
            msg = state_data.get('msg')
            await msg.edit_text("💱Введите курс OPEN к рублю:\n")
            await state.set_data({'maker': state_data.get('maker'), 'deal_type': state_data.get('deal_type'), 'number': txt, 'msg': msg})
            await state.set_state(MarketStates.addCource)
        else:
            w = await message.answer("❌ Некорректный номер.\n"
                                     "🔄 Попробуйте еще раз.")
            await state.update_data(ermsg=w)
    except ValueError:
        w = await message.answer("❌ Некорректный номер.\n"
                                 "🔄 Попробуйте еще раз.")
        await state.update_data(ermsg=w)



@router.message(MarketStates.addCource)
async def getmarketcource(message: Message, state: FSMContext):
    try:
        await message.delete()
        ermsg = (await state.get_data()).get('ermsg')
        await ermsg.delete()
    except Exception:
        pass
    try:
        cource = float(message.text)
        if cource > 0:
            state_data = await state.get_data()
            msg = state_data.get('msg')
            await state.set_data({'maker': state_data.get('maker'), 'deal_type': state_data.get('deal_type'), 'number': state_data.get('number'), 'cource': cource, 'msg': msg})
            await msg.edit_text(f'💲 Введите сумму минимальной сделки в OPEN(Не меньше {config.MIN_DEAL}):')
            await state.set_state(MarketStates.minCource)
        else:
            w = await message.answer("❌ Некорректный курс\n"
                                     "💡 Например: 15.63")
            await state.update_data(ermsg=w)
    except ValueError:
        w = await message.answer("❌ Некорректный курс\n"
                             "💡 Например: 15.63")
        await state.update_data(ermsg=w)



@router.message(MarketStates.minCource)
async def getmincource(message: Message, state: FSMContext):
    try:
        await message.delete()
        ermsg = (await state.get_data()).get('ermsg')
        await ermsg.delete()
    except TelegramBadRequest:
        pass
    except AttributeError:
        pass
    try:
        min = float(message.text)
        state_data = await state.get_data()
        msg = state_data.get('msg')
        max = udb.get_balance(message.from_user.id)[0]*(1-config.MARKET_MAKER_FEE)
        if config.MIN_DEAL <= min <= max or state_data.get('deal_type') == 'sell':
            await state.set_data({'maker': state_data.get('maker'), 'deal_type': state_data.get('deal_type'),
                                  'number': state_data.get('number'), 'cource': state_data.get('cource'), 'min': min, 'msg': msg})
            await msg.edit_text('📊 Последнее что нужно для \nсоздания сделки это \nмаксимальное кол-во OPEN.\nВведи его(Не меньше минимальной сделки): ')
            await state.set_state(MarketStates.postDeal)
        else:
            w = await message.answer("❌ Некорректная сумма\n"
                                 f"💡 Минимум: {config.MIN_DEAL}\n"
                                 f"💡 Максимум: {max}", reply_markup=skb.get_backmrktbtn_kb())
            await state.update_data(ermsg=w)
    except ValueError:
        w = await message.answer("❌ Некорректная сумма", reply_markup=skb.get_backmrktbtn_kb())
        await state.update_data(ermsg=w)




@router.message(MarketStates.postDeal)
async def market_postdeal(message: Message, state: FSMContext):
    try:
        await message.delete()
        ermsg = (await state.get_data()).get('ermsg')
        await ermsg.delete()
    except TelegramBadRequest:
        pass
    except AttributeError:
        pass
    state_data = await state.get_data()
    try:
        min = state_data.get('min')
        amount = float(message.text)
        if amount >= min:
            max = udb.get_balance(message.from_user.id)[0]*(1-config.MARKET_MAKER_FEE)
            if amount <= max or state_data.get('deal_type') == "sell":
                msg = state_data.get('msg')
                if state_data.get('deal_type') == "buy":
                    deal_type = state_data.get('deal_type')
                    number = state_data.get('number')
                    cource = state_data.get('cource')
                    min = state_data.get('min')
                    dt = datetime.datetime.now()

                    uid = message.from_user.id
                    udb.lock_balance(uid, amount/(1-config.MARKET_MAKER_FEE))
                    dealsdb.add_deal(message.from_user.id, amount, deal_type, number, dt, cource, min)
                    await msg.edit_text("➕ Сделка добавлена.\n"
                                        "🔔 Вы получите уведомление когда кто-либо подтвердит сделку.\n"
                                        "⛔ Средства для безопасности сделки заблокированы.\n"
                                        "🔄 В случае отмены сделки все средства будут возвращены", reply_markup=skb.get_backmrktbtn_kb())
                    await state.clear()
                elif state_data.get('deal_type') == "sell":
                    deal_type = state_data.get('deal_type')
                    number = state_data.get('number')
                    cource = state_data.get('cource')
                    dt = datetime.datetime.now()
                    uid = message.from_user.id
                    min = state_data.get('min')
                    dealsdb.add_deal(message.from_user.id, amount, deal_type, number, dt, cource, min)
                    await msg.edit_text("➕ Сделка добавлена.\n"
                                        "🔔 Вы получите уведомление\n"
                                        "когда кто-либо подтвердит сделку.\n")
                    await state.clear()
            else:
                w = await message.answer("❌ Недостаточно средств\n"
                                     f"💡 Максимум: {max} OPEN\n")
                await state.update_data(ermsg=w)

        else:
            w = await message.answer("❌ Некорректная сумма\n"
                                 "➡️ Введите сумму:")
            await state.update_data(ermsg=w)
    except ValueError:
        w = await message.answer("❌ Некорректная сумма\n"
                             "➡️ Введите сумму:")
        await state.update_data(ermsg=w)
