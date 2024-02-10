from aiogram import Bot
from aiogram.fsm.state import StatesGroup, State
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