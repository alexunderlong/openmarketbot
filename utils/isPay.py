import requests as r
from bot import config

def isPay(comment, amount):
    resp = r.get('https://toncenter.com/api/v2/getTransactions?'
                        f'address={config.DEPOSIT_ADDRESS}&limit=100&'
                        f'archival=true&api_key={config.TONCENTER_API_KEY}').json()
    if not resp['ok']:
        return 'err'

    for tx in resp['result']:
        txt = tx['in_msg']['message']
        value = int(tx['in_msg']['value'])
        if str(txt) == str(comment) and value == amount*1000000000:
            return True

    return False
