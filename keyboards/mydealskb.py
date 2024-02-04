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

            answer += f" {float(deal[9]):.2f}-{deal[3]:.2f} OPEN"
            answer += f" {float(deal[3]) * float(deal[7]):.2f}₽"
            mk.row(InlineKeyboardButton(text=answer, callback_data=f"del:{deal[0]}"))
            answer = ''
    mk.button(text='Назад', callback_data='market')
    return mk.as_markup()
