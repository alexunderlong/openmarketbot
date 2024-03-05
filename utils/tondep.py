import asyncio
import requests
from aiogram import Bot
from aiogram.enums import ParseMode
from aiogram.exceptions import TelegramRetryAfter
from pytonapi.exceptions import TONAPITooManyRequestsError

from bot import config
from pytonapi import AsyncTonapi
from dbs import udb


async def start():
    tonapi = AsyncTonapi(config.TON_API_KEY)
    initlt()
    bot = Bot(token=config.TOKEN)
    while True:
        for shardid in range(len(config.SHARDS_ADDRESS)):
            for token in config.SUPPORT_TOKENS:
                last_lt = int(get_lt(token, shardid))
                if last_lt == 404:
                    print('TOKEN NOT FOUND')
                # jettons
                await asyncio.sleep(2)
                try:
                    history = (await tonapi.accounts.get_jettons_history_by_jetton(config.SHARDS_ADDRESS[shardid],
                                                                                   config.SUPPORT_TOKENS[token],
                                                                                   limit=100,
                                                                                   start_date=last_lt)).dict().get('events')
                except TONAPITooManyRequestsError:
                    await asyncio.sleep(2)
                    history = (await tonapi.accounts.get_jettons_history_by_jetton(config.SHARDS_ADDRESS[shardid],
                                                                                   config.SUPPORT_TOKENS[token],
                                                                                   limit=100,
                                                                                   start_date=last_lt)).dict().get('events')
                history = list(reversed(history))
                for tx in history:
                    lt = tx.get('timestamp')

                    if lt <= int(last_lt):
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

                    if not int(udb.get_user_by_uid(uid)[3]) == int(shardid):
                        continue

                    info = await tonapi.jettons.get_info(config.SUPPORT_TOKENS[token])
                    dec = int(info.dict().get('metadata').get('decimals'))
                    udb.add_balance(uid, value / (10 ** dec), token)

                    if dec not in range(1, 255):
                        continue

                    await bot.send_message(uid, '➡️ Баланс пополнен!\n'
                                                f'*+{(value / (10 ** dec)):.2f} {token}*',
                                           parse_mode=ParseMode.MARKDOWN)

                    last_lt = lt
                    setlt(token, last_lt, shardid)
                # ton
            last_lt = get_lt('TON', shardid)
            resp = requests.get(f'{config.API_BASE_URL}/api/v2/getTransactions?'
                                f'address={config.SHARDS_ADDRESS[shardid]}&limit=100&lt={last_lt}&'
                                f'archival=true&api_key={config.TONCENTER_API_KEY}').json()

            if not resp['ok']:

                continue
            resp['result'] = list(reversed(resp['result']))
            for tx in resp['result']:
                lt = int(tx['transaction_id']['lt'])
                if lt <= int(last_lt):
                    continue

                value = int(tx['in_msg']['value'])
                if value > 0:
                    uid = tx['in_msg']['message']
                    if not uid.isdigit():
                        continue

                    uid = int(uid)

                    if not udb.check_user(uid):
                        continue

                    if not int(udb.get_user_by_uid(uid)[3]) == int(shardid):
                        continue

                    udb.add_balance(uid, value / 1e9, "TON")
                    try:
                        await bot.send_message(uid, '➡️ Баланс пополнен!\n'
                                                    f'*+{(value / 1e9):.2f} TON*',
                                               parse_mode=ParseMode.MARKDOWN)
                    except TelegramRetryAfter:
                        await asyncio.sleep(10)
                    last_lt = lt
                    setlt('TON', last_lt, shardid)


def initlt():
    try:
        tokens = list(config.SUPPORT_TOKENS.keys())
        lines = []
        with open('utils/.txt/last_lt.txt', 'r') as f:

            tokens.append('TON')
            for line in f.readlines():
                for char in line:
                    if char in " :1234567890\n":
                        line = line.replace(char, '')
                lines.append(line)
        dif = [x for x in tokens if x not in lines]
        if len(dif) != 0:

            with open('utils/.txt/last_lt.txt', 'r') as file:
                 data = file.read()
            with open('utils/.txt/last_lt.txt', 'w') as file:
                length = len(config.SHARDS_ADDRESS)-1
                for t in dif:
                    writedata = ''
                    while length >= 0:
                        writedata += f'{length}{t}: 0\n'
                        length -= 1
                    file.write(data + writedata)

    except FileNotFoundError:
        length = len(config.SHARDS_ADDRESS)-1

        lt = ''
        while length >= 0:
            lt += f'{length}TON: 0\n'
            for token in config.SUPPORT_TOKENS:
                lt += f'{length}{token}: 0\n'
            length -= 1
        with open('utils/.txt/last_lt.txt', 'w') as file:
            file.write(lt)



def setlt(token, lt, shardid):
    with open("utils/.txt/last_lt.txt", 'r') as f:
        lines = f.readlines()
        for line in range(len(lines)):
            if str(lines[line].split(':')[0]) == f"{shardid}{token}":
                lines[line] = lines[line].split(' ')[0]+f' {lt}{'\n' if line < len(lines) else ''}'

    with open("utils/.txt/last_lt.txt", 'w') as f:
        f.writelines(lines)


def get_lt(token, shardid):
    with open('utils/.txt/last_lt.txt', 'r') as f:
        for lt in f.readlines():
            lt = lt.removeprefix(str(shardid))
            if lt.startswith(token):
                return lt.removeprefix(token+': ').removeprefix('TON: ').replace('\n', '')
    return 404


if __name__ == "__main__":
    asyncio.run(start())
