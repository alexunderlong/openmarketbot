from bot.config import DB_USER, DB_HOST, DB_NAME, DP_PASS
import psycopg2


conn = psycopg2.connect(f"dbname={DB_NAME} user={DB_USER} host={DB_HOST} password={DP_PASS}")
conn.autocommit = True

with conn.cursor() as cursor:
     cursor.execute(
         """CREATE TABLE IF NOT EXISTS Cheques(
             id bigint DEFAULT -1,
             uid TEXT NOT NULL,
             amount TEXT NOT NULL,
             token TEXT NOT NULL,
             active BOOLEAN DEFAULT TRUE,
             salt TEXT NOT NULL);""")


def add_cheq(uid, amount, token, salt):
    with conn.cursor() as cur:
        cur.execute(f'INSERT INTO Cheques (uid, amount, token, salt) VALUES (%s, %s, %s, %s);', (uid, amount, token, salt))
        cur.execute('select row_number() over(order by id), * from  ( select * from Cheques)')
        fetch = cur.fetchall()
        id = fetch[len(fetch) - 1][0]
        cur.execute(f'UPDATE Cheques SET id = {id} WHERE id = -1')
        return id


def set_cheq_inactive(id):
    with conn.cursor() as cur:
        cur.execute(f'UPDATE Cheques SET active = False WHERE id = {id}')


def set_cheq_status(id):
    with conn.cursor() as cur:
        cur.execute(f'SELECT active FROM Cheques WHERE id = {id}')
        return cur.fetchone()[0]


def get_cheq(id):
    with conn.cursor() as cur:
        cur.execute(f'SELECT * FROM Cheques WHERE id = {id}')
        return cur.fetchone()


def get_cheques_by_uid(uid):
    with conn.cursor() as cur:
        cur.execute(f'SELECT * FROM Cheques WHERE uid = %s', (str(uid),))
        return cur.fetchall()

