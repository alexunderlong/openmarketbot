import sqlite3


con = sqlite3.connect('dbs/dealsdb.sqlite', timeout=60.00)
cur = con.cursor()


cur.execute('''CREATE TABLE IF NOT EXISTS Deals (
                id INTEGER ,
                makerid INTEGER,
                type TEXT,
                amount INTEGER,
                makersnum TEXT,
                dtadd TEXT,
                dtend TEXT ,
                cource TEXT,
                takerid INTEGER,
                minamount TEXT,
                takeramount TEXT
            )''')
con.commit()


def add_deal(uid, amount, type, num, dtadd, cource, minamount):
    cur.execute('INSERT INTO Deals VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)', (-1, int(uid), type, amount, num, dtadd, "", f"{cource}", 0, f"{minamount}", "",))
    con.commit()
    rowid = cur.lastrowid
    cur.execute(f'UPDATE Deals SET id = {rowid} WHERE id = -1')
    con.commit()


def get_deals_by_makerid(uid):
    cur.execute(f'SELECT * FROM Deals WHERE makerid = {uid}')
    deals = cur.fetchall()
    return deals


def get_deals_by_type(type):
    cur.execute(f'SELECT * FROM Deals WHERE type = ?', (f"{type}",))
    deals = cur.fetchall()
    return deals


def set_takerid_by_id(id, takerid):
    cur.execute(f'UPDATE Deals SET takerid = {takerid} WHERE id = {id}')
    con.commit()


def set_takeramount_by_id(id, takeramount):
    cur.execute(f'UPDATE Deals SET takeramount = {f'{takeramount}'} WHERE id = {id}')
    con.commit()

def set_deal_hide(id):
    cur.execute(f'UPDATE Deals SET dtend = ? WHERE id = {id}', ('hide',))
    con.commit()

def set_deal_active(id):
    cur.execute(f'UPDATE Deals SET dtend = ? WHERE id = {id}', ('',))
    con.commit()


def get_deal_by_id(id):
    cur.execute(f'SELECT * FROM Deals WHERE id = ?', (id,))
    deal = cur.fetchone()
    return deal


def set_takernum_by_id(id, num):
    cur.execute(f'UPDATE Deals SET makersnum = ?  WHERE id = {id}', (num,))
    con.commit()


def rem_amount_by_id(id, amount):
    cur.execute(f'UPDATE Deals SET amount = amount - {amount} WHERE id = {id}')
    con.commit()
