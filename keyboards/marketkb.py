from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def get_market_kb():
    btnbuy = InlineKeyboardButton(text='Купить📈', callback_data='buy')
    btnsell = InlineKeyboardButton(text='Продать📉', callback_data='sell')
    btnmydeals = InlineKeyboardButton(text='Мои обьявления📄', callback_data='mydeals')
    btnmakedeals = InlineKeyboardButton(text='Создать сделку💸', callback_data='makedeal')
    btnback = InlineKeyboardButton(text='Назад⬅️', callback_data='start')

    mk_b = InlineKeyboardMarkup(row_width=2,
                                inline_keyboard=[[btnbuy, btnsell, ], [btnmydeals], [btnmakedeals], [btnback], ])
    return mk_b
