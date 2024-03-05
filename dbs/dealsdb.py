import datetime
import json
from types import NoneType

import utils.settings
from bot.config import DB_USER, DB_HOST, DB_NAME, DP_PASS
import psycopg2

from dbs import udb

conn = psycopg2.connect(f"dbname={DB_NAME} user={DB_USER} host={DB_HOST} password={DP_PASS}")
conn.autocommit = True

with conn.cursor() as cursor:
    cursor.execute(
        """CREATE TABLE IF NOT EXISTS Deals(
                id bigint,
                makerid bigint,
                type TEXT,
                amount FLOAT,
                makersnum TEXT,
                dts JSON,
                status TEXT ,
                cource TEXT,
                takerid bigint,
                minamount TEXT,
                takeramount TEXT,
                payments TEXT);""")


def add_deal(uid, amount, type, num, dt, cource, minamount, payments):
    with conn.cursor() as cur:
        uid = str(uid)
        dts = json.dumps({"dt": {"addtime": str(dt)}})
        cur.execute(
            'INSERT INTO Deals (id, makerid, type, amount, makersnum, dts, status, cource, takerid, minamount, takeramount, payments) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)',
            (-1, int(uid), type, amount, num, dts, "", f"{cource}", 0, f"{minamount}", "", payments))
        cur.execute('select row_number() over(order by id), * from  ( select * from deals)')
        fetch = cur.fetchall()
        rowid = fetch[len(fetch) - 1][0]
        cur.execute(f'UPDATE Deals SET id = {rowid} WHERE id = -1')


def set_to_dts_timestart(id, dt, uid, new=False):
    with conn.cursor() as cur:
        uid = str(uid)
        dts = getdtsbyid(id)
        try:
            dts[uid]['launch'] = str(dt)
        except:
            dts[uid] = {'launch': str(dt)}
        if new:
            dts[uid] = {'launch': str(dt)}
        dts = json.dumps(dts)
        cur.execute(f'UPDATE Deals SET dts = %s WHERE id = {id}', (dts,))


def get_all_user_deals_id(uid):
    with conn.cursor() as cur:
        cur.execute(f'SELECT id FROM Deals WHERE makerid = {uid}')
        dealsids = [did[0] for did in cur.fetchall()]
        cur.execute(f"SELECT id FROM Deals WHERE (dts->'{str(uid)}') IS NOT NULL;")
        takerdealsids = [did[0] for did in cur.fetchall()]
        dealsids.extend(takerdealsids)
        return dealsids


def get_deals_by_listid(ids: list):
    with conn.cursor() as cur:
        cur.execute(f'SELECT * FROM Deals WHERE id = ANY(%s)', (ids,))
        deals = cur.fetchall()
        return deals


def set_to_dts_time_end(id, dt, uid):
    with conn.cursor() as cur:
        uid = str(uid)
        dts = getdtsbyid(id)
        dts[uid]['end'] = str(dt)
        dts = json.dumps(dts)
        cur.execute(f'UPDATE Deals SET dts = %s WHERE id = {id}', (dts,))


def set_to_dts_success(id, uid, isSuccess):
    with conn.cursor() as cur:
        uid = str(uid)
        dts = getdtsbyid(id)
        dts[uid]['isSuccess'] = isSuccess
        dts = json.dumps(dts)
        cur.execute(f'UPDATE Deals SET dts = %s WHERE id = {id}', (dts,))


def set_to_dts_stage(id, uid, stage):
    with conn.cursor() as cur:
        dts = getdtsbyid(id)
        uid = str(uid)
        dts[uid]['stage'] = str(stage)
        dts = json.dumps(dts)
        cur.execute(f'UPDATE Deals SET dts = %s WHERE id = {id}', (dts,))


def getdtsbyid(id):
    with conn.cursor() as cur:
        cur.execute(f'SELECT dts FROM Deals WHERE id = {id}')
        dts = cur.fetchone()[0]
        return dts


def get_deals_by_makerid(uid):
    with conn.cursor() as cur:
        uid = str(uid)
        cur.execute(f'SELECT * FROM Deals WHERE makerid = {uid}')
        deals = cur.fetchall()
        return deals


def get_deals_by_type(type):
    with conn.cursor() as cur:
        cur.execute(f'SELECT * FROM Deals WHERE type = %s', (type,))
        deals = cur.fetchall()
        return deals


def set_takerid_by_id(id, takerid):
    with conn.cursor() as cur:
        cur.execute(f'UPDATE Deals SET takerid = {takerid} WHERE id = {id}')


def set_takeramount_by_id(id, takeramount):
    with conn.cursor() as cur:
        cur.execute(f'UPDATE Deals SET takeramount = {takeramount} WHERE id = {id}')

def set_deal_hide(id):
    with conn.cursor() as cur:
        cur.execute(f'UPDATE Deals SET status = %s WHERE id = {id}', ('hide',))


def set_deal_active(id):
    with conn.cursor() as cur:
        cur.execute(f'UPDATE Deals SET status = %s WHERE id = {id}', ('',))


def set_deal_inactive(id):
    with conn.cursor() as cur:
        cur.execute(f'UPDATE Deals SET status = %s WHERE id = {id}', ('inactive',))


def get_deal_by_id(id):
    with conn.cursor() as cur:
        cur.execute(f'SELECT * FROM Deals WHERE id = %s', (id,))
        deal = cur.fetchone()
        return deal


def set_takernum_by_id(id, num):
    with conn.cursor() as cur:
        cur.execute(f'UPDATE Deals SET makersnum = %s  WHERE id = {id}', (num,))


def rem_amount_by_id(id, amount):
    with conn.cursor() as cur:
        cur.execute(f'UPDATE Deals SET amount = amount - {amount} WHERE id = {id}')

def get_all_deals():
    with conn.cursor() as cur:
        cur.execute(f'SELECT * FROM Deals ', )
        deals = cur.fetchall()
        return deals


async def check_deal_time():
    while True:
        deals = get_all_deals()
        for deal in deals:
            id = deal[0]
            try:
                dts = getdtsbyid(id)
                for uid in dts:
                    if uid != 'dt':
                        if not isinstance(dts[uid].get('launch'), NoneType):
                            launchdts = datetime.datetime.strptime(dts[uid]['launch'], "%Y-%m-%d %H:%M:%S.%f")
                            if not isinstance(dts[uid].get('end'), NoneType):
                                endhdts = datetime.datetime.strptime(dts[uid]['end'], "%Y-%m-%d %H:%M:%S.%f")
                                if launchdts + datetime.timedelta(minutes=20) < endhdts and not dts[uid].get('isSuccess') is False:
                                    set_to_dts_success(id, uid, False)
                                    if deal[2] == 'sell':
                                        udb.relock_balance(uid, deal[10], 'OPEN')
                                        await utils.settings.bot.send_message(chat_id=uid, text='Время сделки истекло. Средства возвращены на баланс')
                                    else:
                                        await utils.settings.bot.send_message(uid, 'Время сделки истекло')
                                    await utils.settings.bot.send_message(deal[1], 'Время сделки истекло')
                                    set_deal_active(id)



                            elif launchdts + datetime.timedelta(minutes=20) < datetime.datetime.now() and not dts[uid].get('isSuccess') is False:
                                set_to_dts_success(id, uid, False)
                                set_deal_active(id)
                                if deal[2] == 'sell':
                                    udb.relock_balance(uid, deal[10], 'OPEN')
                                    await utils.settings.bot.send_message(uid, 'Время сделки истекло. Средства возвращены на баланс')
                                else:
                                    await utils.settings.bot.send_message(uid, 'Время сделки истекло')
                                await utils.settings.bot.send_message(deal[1], 'Время сделки истекло')
            except TypeError:
                pass
