import asyncio
from aiogram import Dispatcher
from aiogram.fsm.storage.redis import RedisStorage
from bot.config import REDIS_STORAGE_URL
from handlers import start, callback, market, withdraw, cheques
from utils.settings import bot, ThrottlingMiddleware


async def main():
    storage = RedisStorage.from_url(REDIS_STORAGE_URL)
    dp = Dispatcher(storage=storage)
    dp.include_routers(start.router, callback.router, market.router, withdraw.router, cheques.router)
    dp.message.middleware.register(ThrottlingMiddleware(storage=storage))
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
