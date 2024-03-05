from aiogram import Router
from aiogram.enums import ParseMode
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
    id = data.get('id')
    msg = data.get('msg')
    deal = dealsdb.get_deal_by_id(id)
    if deal[6] == 'hide' and not dealsdb.getdtsbyid(id)[str(deal[8])].get('stage') == 0 and not dealsdb.getdtsbyid(id)[str(deal[8])].get('stage') == 2 and not dealsdb.getdtsbyid(id)[str(deal[8])].get('stage') == 0:
        try:
            await message.delete()
            w = data.get('errmsg')
            await bot.delete_message(chat_id=w[1], message_id=w[0])
        except:
            pass

        txt = str(message.text)
        result = re.match(r'^(\+7|7|8)?[\s\-]?\(?[489][0-9]{2}\)?[\s\-]?[0-9]{3}[\s\-]?[0-9]{2}[\s\-]?[0-9]{2}$', txt)
        if(bool(result)):

            dealsdb.set_takernum_by_id(id, txt)
            deal = dealsdb.get_deal_by_id(id)
            num = deal[4]
            amrub = float(deal[10]) * float(deal[7])
            dealsdb.set_to_dts_stage(id, deal[8], 2)
            dealsdb.set_to_dts_time_end(id, datetime.datetime.now(), deal[8])
            await bot.edit_message_text(text="✅ Номер принят. \n🕓 Ожидайте подтверждение перевода от продавца", parse_mode=ParseMode.MARKDOWN, chat_id=msg[1], message_id=msg[0], reply_markup=skb.get_sup_kb())
            await bot.send_message(chat_id=deal[1],
                                   text=f'📤Вам нужно перевести <code>{amrub :.2f}</code>₽ по {deal[11]} на номер телефона <code>{num}</code> с комментарием <code>Сделка на OpenMarket #{str(deal[0])}</code>. После чего нажать "Подтвердить перевод"',
                                   reply_markup=skb.get_TKgetnum_kb(id),
                                   parse_mode=ParseMode.HTML)
        else:
            w = await message.answer("❌ Неправильный номер номер телефона. Попробуйте еще.")
            await state.update_data(errmsg=(w.message_id, w.chat.id))
    else:
        try:
            await bot.edit_message_text(text='❌ Время истекло', reply_markup=skb.get_backmrktbtn_kb(), chat_id=msg[1], message_id=msg[0])
        except:
            await bot.send_message(chat_id=message.from_user.id, text='❌ Время истекло', reply_markup=skb.get_backmrktbtn_kb())


@router.message(MarketStates.chooseAmount)
async def chooseAmount(message: Message, state: FSMContext):
    data = await state.get_data()
    await message.delete()
    try:

        w = data.get('ermsg')
        await bot.delete_message(chat_id=w[1], message_id=w[0])
    except:
        pass
    try:
        buyamount = float(message.text)

        uid = message.from_user.id
        id = data.get('id')
        deal = dealsdb.get_deal_by_id(id)
        min = float(deal[9])
        max = float(deal[3])
        makerid = deal[1]
        status = deal[6]
        if min <= buyamount <= max:
            if makerid != uid:
                if data.get('deal_type') == 'sell' and float(buyamount) > float(udb.get_balance(uid).get("OPEN")):
                        w = await message.answer("❌ Недостаточно средств")
                        await state.update_data(ermsg=(w.message_id, w.chat.id))
                else:
                    if not status == 'hide' or not status == 'inactive':
                        del_msg = data.get('del_msg')
                        await bot.delete_message(chat_id=del_msg[1], message_id=del_msg[0])
                        dealsdb.set_takerid_by_id(id, uid)
                        dealsdb.set_deal_hide(id)
                        dealsdb.set_takeramount_by_id(id, buyamount)
                        await state.set_state(MarketStates.MarketMenu)
                        dealsdb.set_to_dts_timestart(deal[0], datetime.datetime.now(), uid, True)
                        if data.get('deal_type') == 'sell':
                            await message.answer("⛔ На момент сделки мы залокировали OPEN на кошелеке\n🕓Ожидаем ответа продавца", reply_markup=skb.get_sup_kb())
                            udb.lock_balance(uid, buyamount, "OPEN")
                            await bot.send_message(makerid, f"🚀Пользователь начал с вами сделку на продажу {buyamount} OPEN по курсу {deal[7]} RUB/OPEN", reply_markup=skb.get_acceptMK_kb(id))
                        else:
                            await message.answer("🕓 Ожидаем ответа продавца" , reply_markup=skb.get_sup_kb())
                            await bot.send_message(makerid, f"🚀 Пользователь начал с вами сделку на покупку {buyamount} OPEN по курсу {deal[7]} RUB/OPEN", reply_markup=skb.get_acceptMK_kb(id))
                    else:
                        await message.edit_text(text='Обьявление неактуально или пользователь проводит сделку с другим пользователем', reply_markup=skb.get_backmrktbtn_kb())
            else:
                w = await message.answer("❌ Вы не можете начать сделку с самим собой.", reply_markup=skb.get_backmrktbtn_kb())
                await state.update_data(ermsg=(w.message_id, w.chat.id))
        else:
            w = await message.answer("❌ Не соблюдены условия сделки", reply_markup=skb.get_backmrktbtn_kb())
            await state.update_data(ermsg=(w.message_id, w.chat.id))
    except ValueError:
        w = await message.answer("❌ Некорректная сумма", reply_markup=skb.get_backmrktbtn_kb())
        await state.update_data(ermsg=(w.message_id, w.chat.id))





@router.message(MarketStates.PaymentsNum)
async def getmarketnum(message: Message, state: FSMContext):
    try:
        await message.delete()
        data = await state.get_data()
        w = data.get('w')
        await bot.delete_message(chat_id=w[1], message_id=w[0])
    except Exception:
        pass
    try:
        txt = str(message.text)
        result = re.match(r'^(\+7|7|8)?[\s\-]?\(?[489][0-9]{2}\)?[\s\-]?[0-9]{3}[\s\-]?[0-9]{2}[\s\-]?[0-9]{2}$', txt)

        if bool(result):
            state_data = await state.get_data()
            msg = state_data.get('msg')
            await bot.edit_message_text(text="💱Введите курс OPEN к рублю:\n", message_id=msg[0], chat_id=msg[1])
            await state.update_data(number=txt, msg=msg)
            await state.set_state(MarketStates.addCource)
        else:
            w = await message.answer("❌ Некорректный номер.\n"
                                     "🔄 Попробуйте еще раз.")
            wchatid = w.chat.id
            wid = w.message_id
            await state.update_data(w=(w.message_id, w.chat.id))
    except ValueError:
        w = await message.answer("❌ Некорректный номер.\n"
                                 "🔄 Попробуйте еще раз.")
        await state.update_data(w=(w.message_id, w.chat.id))



@router.message(MarketStates.addCource)
async def getmarketcource(message: Message, state: FSMContext):
    try:
        await message.delete()
        err = (await state.get_data()).get('ermsg')
        await bot.delete_message(chat_id=err[1], message_id=err[0])
    except Exception:
        pass
    try:
        cource = float(message.text)
        if cource > 0:
            state_data = await state.get_data()
            msg = state_data.get('msg')
            await state.update_data(cource=cource, msg=msg)
            await bot.edit_message_text(text=f'💲 Введите сумму минимальной сделки в OPEN(Не меньше {config.MIN_DEAL}):', message_id=msg[0], chat_id=msg[1])
            await state.set_state(MarketStates.minCource)
        else:
            w = await message.answer("❌ Некорректный курс\n"
                                     "💡 Например: 15.63")
            await state.update_data(ermsg=(w.message_id, w.chat.id))
    except ValueError:
        w = await message.answer("❌ Некорректный курс\n"
                             "💡 Например: 15.63")
        await state.update_data(ermsg=(w.message_id, w.chat.id))



@router.message(MarketStates.minCource)
async def getmincource(message: Message, state: FSMContext):
    try:
        await message.delete()
        err = (await state.get_data()).get('ermsg')
        await bot.delete_message(chat_id=err[1], message_id=err[0])
    except:
        pass
    try:
        min = float(message.text)
        state_data = await state.get_data()
        msg = state_data.get('msg')
        max = udb.get_balance(message.from_user.id).get("OPEN")
        if config.MIN_DEAL <= min <= max or state_data.get('deal_type') == 'sell':
            await state.update_data(min=min, msg=msg)
            await bot.edit_message_text(text='📊 Последнее что нужно для \nсоздания сделки это \nмаксимальное кол-во OPEN.\nВведи его(Не меньше минимальной сделки): ', message_id=msg[0], chat_id=msg[1])
            await state.set_state(MarketStates.postDeal)
        else:
            w = await message.answer("❌ Некорректная сумма\n"
                                 f"💡 Минимум: {config.MIN_DEAL}\n"
                                 f"💡 Максимум: {max}", reply_markup=skb.get_backmrktbtn_kb())
            await state.update_data(ermsg=(w.message_id, w.chat.id))
    except ValueError:
        w = await message.answer("❌ Некорректная сумма", reply_markup=skb.get_backmrktbtn_kb())
        await state.update_data(ermsg=(w.message_id, w.chat.id))




@router.message(MarketStates.postDeal)
async def market_postdeal(message: Message, state: FSMContext):
    try:
        await message.delete()
        err = (await state.get_data()).get('ermsg')
        await bot.delete_message(chat_id=err[1], message_id=err[0])
    except:
        pass
    state_data = await state.get_data()
    try:
        min = state_data.get('min')
        amount = float(message.text)
        if amount >= min:
            max = udb.get_balance(message.from_user.id).get("OPEN")
            if amount <= max or state_data.get('deal_type') == "sell":
                msg = state_data.get('msg')
                await state.update_data(amount=amount)
                await state.update_data(uid=message.from_user.id)
                dt = datetime.datetime.now()
                cur = str(dt.year) + str(dt.month) + str(dt.day) + str(dt.hour) + str(dt.minute) + str(dt.second) + str(
                    dt.microsecond)
                curdepid = cur + str(message.from_user.id)
                await state.update_data(curdepid=curdepid)
                await bot.edit_message_text(text='💳 Оплатите счет, что бы ваше обьявление было добавлено в наш маркет',
                                    reply_markup=skb.get_pay_deal_kb(curdepid), chat_id=msg[1], message_id=msg[0])
                await state.set_state(MarketStates.payDeal)

            else:
                w = await message.answer("❌ Недостаточно средств\n"
                                     f"💡 Максимум: {max} OPEN\n")
                await state.update_data(ermsg=(w.message_id, w.chat.id))

        else:
            w = await message.answer("❌ Некорректная сумма\n"
                                 "➡️ Введите сумму:")
            await state.update_data(ermsg=(w.message_id, w.chat.id))
    except ValueError:
        w = await message.answer("❌ Некорректная сумма\n"
                             "➡️ Введите сумму:")
        await state.update_data(ermsg=(w.message_id, w.chat.id))

