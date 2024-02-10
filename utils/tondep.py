import asyncio
from aiogram import Bot
from aiogram.enums import ParseMode

from bot import config
from pytonapi import AsyncTonapi

from dbs import udb


async def start():
    print('TONDEPMODULE STARTED')
    tonapi = AsyncTonapi(config.TON_API_KEY)

    try:
        with open('utils/last_lt.txt', 'r') as f:
            last_lt = int(f.read())
    except FileNotFoundError:
        last_lt = 0

    bot = Bot(token=config.TOKEN)

    while True:

        await asyncio.sleep(2)
        try:
            history = (await tonapi.accounts.get_jettons_history_by_jetton(config.DEPOSIT_ADDRESS, config.OPEN_MASTER_ADDRESS, limit=100)).dict().get('events')


            for tx in history:
                lt = tx.get('lt')


                if lt <= last_lt:
                    continue

                value = int(tx.get('actions')[0].get('JettonTransfer').get('amount'))
                if value > 0:
                    global uid
                    uid = tx.get('actions')[0].get('JettonTransfer').get('comment')



                if uid is None:
                    uid = ''
                if not uid.isdigit():
                    continue

                uid = int(uid)
                if not udb.check_user(uid):
                    continue

                udb.add_balance(uid, value/ 100000)

                await bot.send_message(uid, '➡️ Баланс пополнен!\n'
                                            f'*+{value / 100000:.2f} OPEN*',
                                    parse_mode=ParseMode.MARKDOWN)

                last_lt = lt
                with open('utils/last_lt.txt', 'w') as f:
                    f.write(str(last_lt))
        except Exception as e:
            print(e)

if __name__ == "__main__":
    asyncio.run(start())
