from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def get_start_kb() -> InlineKeyboardMarkup:
    btndep = InlineKeyboardButton(text='Пополнить ⬇️', callback_data='deposit')
    btnbal = InlineKeyboardButton(text='Баланс 💎', callback_data='balance')
    btnwith = InlineKeyboardButton(text='Вывод ⬆️', callback_data='withdraw')
    btnmrkt = InlineKeyboardButton(text='Маркет 💱', callback_data='market')
    chequebtn = InlineKeyboardButton(text='Чеки 🧾', callback_data='cheque')
    mk_b = InlineKeyboardMarkup(row_width=3, inline_keyboard=[[btndep, btnbal, btnwith], [btnmrkt], [chequebtn]])
    return mk_b
