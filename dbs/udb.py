from bot import config
import sqlite3

con = sqlite3.connect('dbs/udb.sqlite', timeout=60.00)
cur = con.cursor()

cur.execute('''CREATE TABLE IF NOT EXISTS Users (
                uid INTEGER,
                balance INTEGER,
                balancelock INTEGER DEFAULT 0
            )''')
con.commit()


def check_user(uid):
    cur.execute(f'SELECT * FROM Users WHERE uid = {uid}')
    user = cur.fetchone()
    if user:
        return True
    return False


def add_user(uid):
    cur.execute(f'INSERT INTO Users VALUES (?, ?, ?)', (uid, 0, 0))
    con.commit()


def get_balance(uid):
    cur.execute(f'SELECT balance FROM Users WHERE uid = {uid}')
    balance = cur.fetchone()
    return balance


def add_balance(uid, amount):
    cur.execute(f'UPDATE Users SET balance = balance + {amount} WHERE uid = {uid}')
    con.commit()


def rem_balance(uid, amount):
    cur.execute(f'UPDATE Users SET balance = balance - {amount} WHERE uid = {uid}')
    con.commit()


def lock_balance(uid, amount):
    if float(amount) <= float(get_balance(uid)[0]):
        cur.execute(f'UPDATE Users SET balance = balance - {amount} WHERE uid = {uid}')
        cur.execute(f'UPDATE Users SET balancelock = balancelock + {amount} WHERE uid = {uid}')
        con.commit()
        return 200
    else:
        return 404


def relock_balance(uid, amount):
    if float(get_lock(uid)[0]) >= amount:
        cur.execute(f'UPDATE Users SET balance = balance + {amount} WHERE uid = {uid}')
        cur.execute(f'UPDATE Users SET balancelock = balancelock - {amount} WHERE uid = {uid}')
        con.commit()
        return 200
    else:
        return 404


def clearlock_by_id(uid):
    cur.execute(f'UPDATE Users SET balancelock = 0 WHERE uid = {uid}')
    con.commit()


def get_lock(uid):
    cur.execute(f'SELECT balancelock FROM Users WHERE uid = {uid}')
    balance = cur.fetchone()
    return balance


def from_bknclock_to_anuser(amount, uid, anuid):
    if float(get_lock(uid)[0]) >= float(amount) / float(1 - config.MARKET_MAKER_FEE):
        cur.execute(f'UPDATE Users SET balancelock = balancelock - {float(amount) / float(1 - config.MARKET_MAKER_FEE)} WHERE uid = {uid}')
        cur.execute(f'UPDATE Users SET balance = balance + {amount} WHERE uid = {anuid}')
        con.commit()
        return 200
    else:
        return 404
