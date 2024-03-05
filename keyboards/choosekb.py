from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

import bot.config as cfg


def get_tokens_kb_for_dep(isDep: bool):
    pref = 'dep' if isDep else 'wd'
    tokens_kb = InlineKeyboardBuilder()
    tonbtn = InlineKeyboardButton(text='TON', callback_data=f'{pref}:TON')
    tokens_kb.row(tonbtn)
    for token in cfg.SUPPORT_TOKENS:
        btn = InlineKeyboardButton(text=token, callback_data=f'{pref}:'+token)
        tokens_kb.row(btn)
    backbtn = InlineKeyboardButton(text='Назад 🔙', callback_data='start')
    tokens_kb.row(backbtn)
    return tokens_kb.as_markup()


def get_tokens_kb_for_cheque():
    tokens_kb = InlineKeyboardBuilder()
    tonbtn = InlineKeyboardButton(text='TON', callback_data=f'cheque:TON')
    tokens_kb.row(tonbtn)
    for token in cfg.SUPPORT_TOKENS:
        btn = InlineKeyboardButton(text=token, callback_data=f'cheque:'+token)
        tokens_kb.row(btn)
    backbtn = InlineKeyboardButton(text='Назад 🔙', callback_data='start')
    tokens_kb.row(backbtn)
    return tokens_kb.as_markup()