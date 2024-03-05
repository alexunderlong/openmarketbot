from typing import Any, Awaitable, Callable, Dict
from aiogram import Bot, BaseMiddleware
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.storage.redis import RedisStorage
from aiogram.types import Message, TelegramObject
from bot import config

bot = Bot(token=config.TOKEN)

class WithdrawStates(StatesGroup):
    getsum = State()
    getaddr = State()


class MarketStates(StatesGroup):
    MarketMenu = State()
    MyDeals = State()
    MakeDeal = State()
    BuyorSell = State()
    Sell = State()
    Buy = State()
    PaymentsNum = State()
    ActiveDeals = State()
    EndDeal = State()
    appealDeal = State()
    payDeal = State()
    postDeal = State()
    addCource = State()
    minCource = State()
    chooseAmount = State()
    TKsendnum = State()


class ChequesStates(StatesGroup):
    getAmount = State()
    acceptCheque = State()



class ThrottlingMiddleware(BaseMiddleware):
    def __init__(self, storage: RedisStorage):
        self.storage = storage

    async def __call__(self,
                       handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
                       event: Message,
                       data: Dict[str, Any]
                       ) -> Any:
        user = f'user{event.from_user.id}'

        check_user = await self.storage.redis.get(name=user)

        if check_user:
            if user != f'user{config.BOT_ID}':
                await bot.delete_message(event.chat.id, event.message_id)
            if int(check_user.decode()) == 1:
                await self.storage.redis.set(name=user, value=0, ex=config.RATE_LIMIT)
                msg = await event.answer(f'Ждите {config.RATE_LIMIT} секунды, затем повторите запрос.')
                state = data.get('state')
                await state.update_data(warnmsgid=msg.message_id, warnchatid=msg.chat.id)
                return msg
            return
        state = await data.get('state').get_data()
        msgid = state.get('warnmsgid')
        chatid = state.get('warnchatid')
        try:
            await bot.delete_message(chatid, msgid)
        except:
            pass
        await self.storage.redis.set(name=user, value=1, ex=config.RATE_LIMIT)

        return await handler(event, data)