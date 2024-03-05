from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from bot.config import SUPPORT_TOKENS, SUPPORT_USERNAME
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
    mk.button(text="Подтвердить перевод ✅", callback_data=f"MK_accept_deal:{id}")
    mk.button(text='Техподдержка 🛠️', url='t.me/' + SUPPORT_USERNAME)
    return mk.as_markup()


def get_sendnum_kb(id):
    mk = InlineKeyboardBuilder()
    mk.button(text="Подтвердить перевод ✅", callback_data=f"TK_accept_trans:{id}")
    mk.button(text='Техподдержка 🛠️', url='t.me/' + SUPPORT_USERNAME)
    return mk.as_markup()


def get_MK_accept_trans_kb(id):
    mk = InlineKeyboardBuilder()
    mk.button(text="Подтвердить перевод ✅", callback_data=f"TK_accept_deal:{id}")
    mk.button(text='Техподдержка 🛠️', url='t.me/' + SUPPORT_USERNAME)
    return mk.as_markup()


def get_market_makedeal_kb():
    btnbuy = InlineKeyboardButton(text='Купить 📈', callback_data='buy')
    btnsell = InlineKeyboardButton(text='Продать 📉', callback_data='sell')
    btnback = InlineKeyboardButton(text='Назад ⬅️', callback_data='market')
    mk_b = InlineKeyboardMarkup(row_width=2, inline_keyboard=[[btnbuy, btnsell, ], [btnback,]])
    return mk_b


def get_calldep_kb(uid, key, shardid):
    keyboard = InlineKeyboardBuilder()
    if key == 'TON':
        keyboard.button(text='Перевести ✅', url=URLbuilder.buildurlforton(str(uid), shardid))
    else:
        keyboard.button(text='Перевести ✅', url=URLbuilder.buildurl(str(uid), SUPPORT_TOKENS[key], shardid))
    keyboard.button(text='Назад ⬅️', callback_data='start')
    return keyboard.as_markup()


def get_backbtn_kb():
    mk_b = InlineKeyboardBuilder()
    mk_b.button(text="Назад ⬅️", callback_data="start")
    return mk_b.as_markup()


def get_cgequesmain_kb():
    mk_b = InlineKeyboardBuilder()
    mk_b.button(text='Создать персональный чек 🧾', callback_data="personalcheque")
    mk_b.row(InlineKeyboardButton(text="Мои чеки 🗄️", callback_data="getcheques"))
    mk_b.row(InlineKeyboardButton(text="Назад ⬅️", callback_data="start"))
    return mk_b.as_markup()


def get_backbtn_with_sup_kb():
    mk_b = InlineKeyboardBuilder()
    mk_b.button(text="Назад ⬅️", callback_data="start")
    mk_b.button(text='Техподдержка 🛠️', url='t.me/'+SUPPORT_USERNAME)
    return mk_b.as_markup()


def get_backmrktbtn_kb():
    mk_b = InlineKeyboardBuilder()
    mk_b.button(text="Назад ⬅️", callback_data="market")
    return mk_b.as_markup()

def get_backundealsbtn_kb():
    mk_b = InlineKeyboardBuilder()
    mk_b.button(text="Назад ⬅️", callback_data="unactive")
    return mk_b.as_markup()


def get_backblnc_kb():
    mk_b = InlineKeyboardBuilder()
    mk_b.button(text="Назад ⬅️", callback_data="balance")
    return mk_b.as_markup()


def get_offer_process_kb(id):
    mk = InlineKeyboardBuilder()
    mk.button(text="Начать сделку ▶️", callback_data=f"startdeal:{id}")
    mk.button(text="Назад ⬅️", callback_data="back_to_offers")
    return mk.as_markup()


def get_accept_addr_kb():
    mk = InlineKeyboardBuilder()
    mk.button(text='ДА ✅', callback_data='transfer')
    mk.button(text='НЕТ ❌', callback_data='start')
    return mk.as_markup()


def get_accept_cheque_kb():
    mk = InlineKeyboardBuilder()
    mk.button(text='Создать чек ✅', callback_data='makepcheque')
    mk.button(text='Назад ⬅️', callback_data='cheque')
    return mk.as_markup()


def get_back_cheque_kb():
    mk = InlineKeyboardBuilder()
    mk.button(text='Назад ⬅️', callback_data='cheque')
    return mk.as_markup()


def get_TKgetnum_kb(id):
    mk = InlineKeyboardBuilder()
    mk.button(text="Подтвердить перевод ✅", callback_data=f"MK_accept_trans:{id}")
    mk.button(text='Техподдержка 🛠️', url='t.me/' + SUPPORT_USERNAME)
    return mk.as_markup()


def get_acceptMK_kb(id):
    mk = InlineKeyboardBuilder()
    mk.button(text="Подтвердить ✅", callback_data=f"accept:{id}")
    mk.button(text="Отклонить ❌", callback_data=f"decline:{id}")
    return mk.as_markup()


def get_pay_deal_kb(comment):
    btnpay = InlineKeyboardButton(text='Оплатить', callback_data='payed')
    btnback = InlineKeyboardButton(text='Назад ⬅️', callback_data='market')
    mk_b = InlineKeyboardMarkup(row_width=2, inline_keyboard=[[btnpay, ], [btnback,]])
    return mk_b


def get_sup_kb():
    mk_b = InlineKeyboardBuilder()
    mk_b.button(text='Техподдержка 🛠️', url='t.me/' + SUPPORT_USERNAME)
    return mk_b.as_markup()


def get_all_cheques(cheques):
    mk = InlineKeyboardBuilder()
    for cheq in cheques:
        mk.row(InlineKeyboardButton(text=f"🗄️ Персональный чек на {cheq[2]} {cheq[3]}", callback_data=f"cheqinfo:{cheq[0]}"))
    mk.row(InlineKeyboardButton(text="🔙 Назад", callback_data="cheque"))
    return mk.as_markup()


def del_cheq(cheqid):
    delcheq = InlineKeyboardButton(text='Удалить чек', callback_data=f'delcheq:{cheqid}')
    cheque = InlineKeyboardButton(text='Назад ⬅️', callback_data='cheque')
    mk_b = InlineKeyboardMarkup(row_width=2, inline_keyboard=[[delcheq, ], [cheque, ]])
    return mk_b
