import json
from types import NoneType

from bot.config import DB_USER, DB_HOST, DB_NAME, DP_PASS
import psycopg2
from bot import config

conn = psycopg2.connect(f"dbname={DB_NAME} user={DB_USER} host={DB_HOST} password={DP_PASS}")
conn.autocommit = True

with conn.cursor() as cursor:
     cursor.execute(
         """CREATE TABLE IF NOT EXISTS Users(
             uid bigint PRIMARY KEY,
             balance JSON NOT NULL,
             lock JSON NOT NULL,
             shardid int NOT NULL);""")


def check_user(uid):
    with conn.cursor() as cur:
        cur.execute(f"SELECT * FROM Users WHERE uid = {uid};")
        user = cur.fetchone()
        if user:
            return True
        return False


def get_all_users():
    with conn.cursor() as cur:
        cur.execute(f'SELECT * FROM Users')
        return cur.fetchall()


def get_user_by_uid(uid):
    with conn.cursor() as cur:
        cur.execute(f'SELECT * FROM Users WHERE uid = {uid}')
        return cur.fetchone()

def add_user(uid):
    s = json.dumps({"TON": 0, "OPEN": 0})
    shardsid = [user[3] for user in get_all_users()]
    stats = {0: 0, 1: 0, 2: 0, 3: 0}
    for shardid in shardsid:
        stats[shardid] += 1
    choosedshardid = min(stats, key=stats.get)
    with conn.cursor() as cur:
        cur.execute(f'INSERT INTO Users (uid, balance, lock, shardid) VALUES (%s, %s, %s, %s);', (uid, s, s, choosedshardid))


def get_balance(uid):
    with conn.cursor() as cur:
        cur.execute(f'SELECT balance FROM Users WHERE uid = {uid};')
        balance = cur.fetchone()[0]
    if isinstance(balance, str):
        balance = json.loads(balance.replace("'", '"'))
    return balance



def get_lock(uid):
    with conn.cursor() as cur:
        cur.execute(f'SELECT lock FROM Users WHERE uid = {uid}')
        lock = cur.fetchone()[0]
    if isinstance(lock, str):
        lock = json.loads(lock.replace("'", '"'))
    return lock

def add_balance(uid, amount, token):
    balance = get_balance(uid)
    if isinstance(balance, str):
        balance = json.loads(balance.replace("'", '"'))
    for key in config.SUPPORT_TOKENS:
        if key == token:
            try:
                balance[token] = float(balance[token]) + amount
            except KeyError:
                balance[token] = amount
    if token == 'TON':
        balance[token] = float(balance[token]) + amount
    with conn.cursor() as cur:
        cur.execute(f'UPDATE Users SET balance = %s WHERE uid = %s', (json.dumps(balance), uid))


def rem_balance(uid, amount, token):
    balance = get_balance(uid)
    balance[token] = float(balance[token]) - amount
    with conn.cursor() as cur:
        cur.execute(f'UPDATE Users SET balance = %s WHERE uid = %s', (json.dumps(balance), uid))


def lock_balance(uid, amount, token):
    amount = float(amount)
    balance = get_balance(uid)
    lock = get_lock(uid)
    if isinstance(balance, str):
        balance = json.loads(balance.replace("'", '"'))

    if isinstance(lock, str):
        lock = json.loads(lock.replace("'", '"'))

    if float(amount) <= float(balance[token]):
        balance[token] = float(balance[token]) - float(amount)
        try:
            lock[token] = float(lock[token]) + amount
        except KeyError:
            lock[token] = amount
        balance = str(balance)
        lock = str(lock)
        with conn.cursor() as cur:
            cur.execute(f'UPDATE Users SET balance = %s WHERE uid = %s', (json.dumps(balance), uid))
            cur.execute(f'UPDATE Users SET lock = %s WHERE uid = %s', (json.dumps(lock), uid))
        return 200
    else:
        return 404


def relock_balance(uid, amount, token):
    amount = float(amount)
    balance = get_balance(uid)
    lock = get_lock(uid)
    if isinstance(balance, str):
        balance = json.loads(balance.replace("'", '"'))

    if isinstance(lock, str):
        lock = json.loads(lock.replace("'", '"'))

    if float(lock[token]) >= float(amount):
        balance[token] = float(balance[token]) + amount
        lock[token] = float(lock[token]) - amount
        balance = str(balance)
        lock = str(lock)
        with conn.cursor() as cur:
            cur.execute(f'UPDATE Users SET balance = %s WHERE uid = %s', (json.dumps(balance), uid))
            cur.execute(f'UPDATE Users SET lock = %s WHERE uid = %s', (json.dumps(lock), uid))
        return 200
    else:
        return 404

def clearlock_by_id(uid, token):
    lock = get_lock(uid)
    balance = get_balance(uid)

    if isinstance(lock, str):
        lock = json.loads(lock.replace("'", '"'))

    if isinstance(balance, str):
        balance = json.loads(balance.replace("'", '"'))
    balance[token] += lock[token]
    lock[token] = 0
    lock = str(lock)
    with conn.cursor() as cur:
        cur.execute(f'UPDATE Users SET balance = %s WHERE uid = %s', (json.dumps(balance), uid))
        cur.execute(f'UPDATE Users SET lock = %s WHERE uid = %s', (json.dumps(lock), uid))


def from_blnclock_to_anuser(amount, uid, anuid, token):
    balance = get_balance(anuid)
    amount = float(amount)
    lock = get_lock(uid)

    if isinstance(lock, str):
        lock = json.loads(lock.replace("'", '"'))

    if isinstance(balance, str):
        balance = json.loads(balance.replace("'", '"'))
    if float(amount) <= float(lock[token]):
        if isinstance(balance.get(token), NoneType):
            balance[token] = float(amount)
        else:
            balance[token] = float(balance[token]) + float(amount)
        lock[token] = float(lock[token]) - float(amount)
        balance = str(balance)
        lock = str(lock)
        with conn.cursor() as cur:
            cur.execute(f'UPDATE Users SET balance = %s WHERE uid = %s', (json.dumps(balance), anuid))
            cur.execute(f'UPDATE Users SET lock = %s WHERE uid = %s', (json.dumps(lock), uid))
        return 200
    else:
        return 404
