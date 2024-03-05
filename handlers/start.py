from aiogram import Router
from aiogram.enums import ParseMode
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from utils.settings import bot
from bot import config
from dbs import udb, chequesdb as chqdb
from keyboards import startkb, smallkbs as skb
from aiogram.utils.deep_linking import decode_payload

router = Router()
starttext = "_Здравствуйте, вас приветствует_ *OpenMarket* _- P2P бот для продажи и покупки токена_ *OPENCOIN*.\n\n"


@router.message(CommandStart())
async def command_start_handler(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    try:
        w = data.get('errmsg')
        await bot.delete_message(chat_id=w[1], message_id=w[0])
    except:
        pass
    current_state = await state.get_state()

    uid = message.from_user.id

    if uid != config.BOT_ID:
        try:
            await bot.delete_message(chat_id=int(data.get('chatid')), message_id=int(data.get('msgid')))
        except:
            pass
        await message.delete()


    if current_state:
        await state.set_state(state=None)
        await state.set_data({'msgid': data.get('msgid'), 'chatid': data.get('chatid')})
    if not udb.check_user(uid) and uid != config.BOT_ID:
        udb.add_user(uid)
    reference = isCheq(message)
    if reference:
        if bool(chqdb.get_cheq(reference.split(':')[0])[4]):
            cheq = chqdb.get_cheq(reference.split(':')[0])
            refsolt = reference.split(':')[1].removeprefix(':')
            chequid = cheq[1]
            if not str(cheq[5]) == str(refsolt):
                w = await bot.send_message(uid, '❌ Данного чека не существует', reply_markup=skb.get_backbtn_kb())
                await state.update_data(errmsg=(w.message_id, w.chat.id))
                return

            if str(chequid) == str(uid):
                await bot.send_message(uid, f'❌ Вы не можете активировать свой чек.\n\nВы можете удалить свой чек в разделе "Мои Чеки" и выбрав чек удалить его. После чего все средства на чеки будут возвращены на ваш баланс.')
            else:
                amount = cheq[2]
                token = cheq[3]
                udb.from_blnclock_to_anuser(amount, chequid, uid, token)
                chqdb.set_cheq_inactive(cheq[0])
                await bot.send_message(chequid, f'<a href="t.me/{message.chat.username}">{message.chat.first_name}</a> активировал ваш чек на сумму {amount} {token}', parse_mode=ParseMode.HTML)
                w = await bot.send_message(uid, f'✔️ Вы активировали чек на сумму {amount} {token}', reply_markup=skb.get_backblnc_kb())
                await state.update_data(errmsg=(w.message_id, w.chat.id))
        else:
            w = await bot.send_message(uid, f'❌ Данный чек уже активирован или удален', reply_markup=skb.get_backbtn_kb())
            await state.update_data(errmsg=(w.message_id, w.chat.id))

    else:
        try:
            await message.edit_text(text=starttext, reply_markup=startkb.get_start_kb(), parse_mode=ParseMode.MARKDOWN)
        except TelegramBadRequest:
            msg = await message.answer(text=starttext, reply_markup=startkb.get_start_kb(), parse_mode=ParseMode.MARKDOWN)
            await state.update_data(msgid=msg.message_id)
            await state.update_data(chatid=msg.chat.id)



def isCheq(message: Message):
    try:
        args = message.text.split(' ')[1]
        reference = decode_payload(args)
        return reference
    except IndexError:
        return
