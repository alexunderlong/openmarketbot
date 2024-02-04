import asyncio
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from handlers import start, callback, market, withdraw
from utils.settings import bot



async def main():
    storage = MemoryStorage()
    dp = Dispatcher(storage=storage)
    dp.include_routers(start.router, callback.router, market.router, withdraw.router)
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
