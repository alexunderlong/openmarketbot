from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder


def offers_kb(posts, n):
    offers_kb = InlineKeyboardBuilder()
    for i in range(n-10, len(posts)):
        if i >= n or i > len(posts):
            break
        else:
            deal = posts[i]
            text = f"{float(deal[9]):.2f}-{float(deal[3]):.2f} OPEN • {float(deal[7]):.2f}₽/$OPEN"
            cur = InlineKeyboardButton(text=text, callback_data="offer_id:"+str(posts[i][0]))
            offers_kb.row(cur)

    if 10 >= n >= len(posts):
        cancel = InlineKeyboardButton(text="Выйти🔙", callback_data="market")
        offers_kb.row(cancel)
    elif n == 10:
        forward = InlineKeyboardButton(text="Вперед➡️", callback_data="forward_offers")
        cancel = InlineKeyboardButton(text="Выйти🔙", callback_data="market")
        offers_kb.row(forward)
        offers_kb.row(cancel)
    elif n >= len(posts):
        back = InlineKeyboardButton(text="Назад⬅️", callback_data="back_offers")
        cancel = InlineKeyboardButton(text="Выйти🔙", callback_data="cancel_offers")
        offers_kb.row(back)
        offers_kb.row(cancel)
    else:
        forward = InlineKeyboardButton(text="Вперед➡️", callback_data="forward_offers")
        back = InlineKeyboardButton(text="Назад⬅️", callback_data="back_offers")
        cancel = InlineKeyboardButton(text="Выйти🔙", callback_data="market")
        offers_kb.row(back, forward)
        offers_kb.row(cancel)
    return offers_kb.as_markup()