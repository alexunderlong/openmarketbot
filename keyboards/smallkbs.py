from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from utils import URLbuilder


def get_sell_offer_accept_kb(id):
    mk = InlineKeyboardBuilder()
    mk.button(text=f"Отправить номер телефона📲", callback_data=f"TKsendnum:{id}")
    return mk.as_markup()

def get_buy_offer_accept_kb(deal):
    mk = InlineKeyboardBuilder()
    mk.button(text=f"{deal[4]}", callback_data="sendnum")
    return mk.as_markup()

def get_TK_accept_trans_kb(id):
    mk = InlineKeyboardBuilder()
    mk.button(text="Подтвердить перевод✅", callback_data=f"MK_accept_deal:{id}")
    return mk.as_markup()

def get_sendnum_kb(id):
    mk = InlineKeyboardBuilder()
    mk.button(text="Подтвердить перевод✅", callback_data=f"TK_accept_trans:{id}")
    return mk.as_markup()

def get_MK_accept_trans_kb(id):
    mk = InlineKeyboardBuilder()
    mk.button(text="Подтвердить перевод✅", callback_data=f"TK_accept_deal:{id}")
    return mk.as_markup()

def get_TK_marketCorB_kb():
    btnokey = InlineKeyboardButton(text='Хорошо🆗', callback_data='okey')
    btnback = InlineKeyboardButton(text='Назад⬅️', callback_data='market')
    mk = InlineKeyboardMarkup(row_width=2, inline_keyboard=[[btnokey], [btnback],])
    return mk

def get_market_makedeal_kb():
    btnbuy = InlineKeyboardButton(text='Купить📈', callback_data='buy')
    btnsell = InlineKeyboardButton(text='Продать📉', callback_data='sell')
    btnback = InlineKeyboardButton(text='Назад⬅️', callback_data='market')
    mk_b = InlineKeyboardMarkup(row_width=2, inline_keyboard=[[btnbuy, btnsell, ], [btnback,]])
    return mk_b

def get_calldep_kb(uid):
    keyboard = InlineKeyboardBuilder()
    keyboard.button(text='Перевести✅', url=URLbuilder.buildurl(str(uid)))
    keyboard.button(text='Назад⬅️', callback_data='start')
    return keyboard.as_markup()

def get_backbtn_kb():
    mk_b = InlineKeyboardBuilder()
    mk_b.button(text="Назад⬅️", callback_data="start")
    return mk_b.as_markup()

def get_backmrktbtn_kb():
    mk_b = InlineKeyboardBuilder()
    mk_b.button(text="Назад⬅️", callback_data="market")
    return mk_b.as_markup()

def get_offer_process_kb(id):
    mk = InlineKeyboardBuilder()
    mk.button(text="Начать сделку▶️", callback_data=f"startdeal:{id}")
    return mk.as_markup()

def get_accept_addr_kb():
    mk = InlineKeyboardBuilder()
    mk.button(text='ДА✅', callback_data='transfer')
    mk.button(text='НЕТ❌', callback_data='start')
    return mk.as_markup()

def get_TKgetnum_kb(id):
    mk = InlineKeyboardBuilder()
    mk.button(text="Подтвердить перевод✅", callback_data=f"MK_accept_trans:{id}")
    return mk.as_markup()

def get_acceptMK_kb(id):
    mk = InlineKeyboardBuilder()
    mk.button(text="Подтвердить✅", callback_data=f"accept:{id}")
    mk.button(text="Отклонить❌", callback_data=f"decline:{id}")
    return mk.as_markup()
