from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from bot.config import SUPPORT_BANKS


def banks_kb(dealslist, n):
    banks = SUPPORT_BANKS
    banks_kb = InlineKeyboardBuilder()
    for i in range(n-5, len(banks)):
        if i >= n or i > len(banks):
            break
        else:
            bank = banks[i]

            bankdeals = [deal for deal in dealslist if deal[11] == bank and deal[6] == '']
            dealsatall = len(bankdeals)
            try:
                price = sorted(bankdeals, key=lambda item: item[7])[0][7]
            except IndexError:
                price = 0

            text = f"{bank} • {dealsatall} • {float(price) :.2f}₽"
            cur = InlineKeyboardButton(text=text, callback_data="bank_id:"+str(i))
            banks_kb.row(cur)

    if 5 >= n >= len(banks):
        cancel = InlineKeyboardButton(text="Выйти 🔙", callback_data="market")
        banks_kb.row(cancel)
    elif n == 5:
        forward = InlineKeyboardButton(text="Вперед ➡️", callback_data="forward_banks")
        cancel = InlineKeyboardButton(text="Выйти 🔙", callback_data="market")
        banks_kb.row(forward)
        banks_kb.row(cancel)
    elif n >= len(banks):
        back = InlineKeyboardButton(text="Назад ⬅️", callback_data="back_banks")
        cancel = InlineKeyboardButton(text="Выйти 🔙", callback_data="market")
        banks_kb.row(back)
        banks_kb.row(cancel)
    else:
        forward = InlineKeyboardButton(text="Вперед ➡️", callback_data="forward_banks")
        back = InlineKeyboardButton(text="Назад ⬅️", callback_data="back_banks")
        cancel = InlineKeyboardButton(text="Выйти 🔙", callback_data="market")
        banks_kb.row(back, forward)
        banks_kb.row(cancel)

    return banks_kb.as_markup()
