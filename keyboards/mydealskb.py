from types import NoneType

from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder


def get_my_deals_kb(mydeals):
    answer = ""
    mk = InlineKeyboardBuilder()
    for deal in mydeals:

        if deal[6] == '':
            if deal[2] == 'sell':
                answer += "📉"
            else:
                answer += "📈"

            answer += f" {float(deal[9]) :.2f}-{deal[3]:.2f} OPEN"
            answer += f" {float(deal[3]) * float(deal[7]):.2f}₽"
            mk.button(text=answer, callback_data=f"del:{deal[0]}")
            answer = ''
    mk.row(InlineKeyboardButton(text='Неактивные обьявления', callback_data='unactive'))
    mk.row(InlineKeyboardButton(text='Назад', callback_data='market'))
    return mk.as_markup()

def get_all_unactive_deals_kb(mydeals):
    answer = ""
    mk = InlineKeyboardBuilder()
    for deal in mydeals:

        if deal[6] == 'inactive':
            if deal[2] == 'sell':
                answer += "📉"
            else:
                answer += "📈"

            answer += f" {float(deal[9]) :.2f}-{deal[3]:.2f} OPEN"
            answer += f" {float(deal[3]) * float(deal[7]):.2f}₽"
            mk.row(InlineKeyboardButton(text=answer, callback_data=f"dealinfo:{deal[0]}"))
            answer = ''
    mk.row(InlineKeyboardButton(text='Назад', callback_data='mydeals'))
    return mk.as_markup()


def get_my_all_deals_kb(deals, uid, isActive):
    mk = InlineKeyboardBuilder()
    uid = str(uid)
    for deal in deals:
        if isActive:
            if deal[6] == 'hide':
                dts = deal[5]
                canadd = canadduid(dts, uid)
                if not canadd and str(deal[1]) == str(uid):
                    for uid in dts:
                        canadd = canadduid(dts, uid)
                        if canadd:
                            break

                if canadd:
                    button_text = f'🟢 {'ПОКУПКА' if deal[2] == 'buy' else 'ПРОДАЖА'} НА {deal[3]} OPEN'
                    mk.row(InlineKeyboardButton(text=button_text, callback_data=f'todeal:{deal[0]}'))

    mk.row(InlineKeyboardButton(text='Назад', callback_data='market'))
    return mk.as_markup()





def canadduid(dts, uid):
    canadd = True
    if isinstance(dts.get(uid), NoneType):
        canadd = False
    else:
        if isinstance(dts[uid].get('launch'), NoneType):
            canadd = False
        if dts[uid].get('stage') == '0' or dts[uid].get('stage') == '4':
            canadd = False
        if not isinstance(dts[uid].get('end'), NoneType) and not dts[uid].get('stage') == '2' and not dts[uid].get('stage') == '3':
            canadd = False

    return canadd

