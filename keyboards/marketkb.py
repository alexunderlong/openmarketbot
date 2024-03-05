from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from bot.config import SUPPORT_USERNAME

def get_market_kb():
    btnbuy = InlineKeyboardButton(text='Купить 📈', callback_data='buy')
    btnsell = InlineKeyboardButton(text='Продать 📉', callback_data='sell')
    btnmydeals = InlineKeyboardButton(text='Мои обьявления 📄', callback_data='mydeals')
    btnallmydeals = InlineKeyboardButton(text='Все сделки 🤝', callback_data='allmydeals')
    btnmakedeals = InlineKeyboardButton(text='Создать сделку 💸', callback_data='makedeal')
    btnback = InlineKeyboardButton(text='Назад ⬅️', callback_data='start')
    btnsup = InlineKeyboardButton(text='Техподдержка 🛠️', url='t.me/'+SUPPORT_USERNAME)

    mk_b = InlineKeyboardMarkup(row_width=2,
                                inline_keyboard=[[btnbuy, btnsell, ], [btnmydeals], [btnallmydeals], [btnmakedeals], [btnsup], [btnback,], ])
    return mk_b
