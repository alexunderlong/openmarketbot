from time import sleep
import requests as r
from bot import config as cfg

hdr = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',
       'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
       'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
       'Accept-Encoding': 'none',
       'Accept-Language': 'en-US,en;q=0.8',
       'Connection': 'keep-alive'}


def getcourcebydior(token: str):
    req = r.get('https://api.dyor.io/api/v3/jettons?address='+token, headers=hdr).json()
    price = req['data']['price']
    return f'{price:.3f}'


def whritecource():
    while True:
        text = ''
        for token in cfg.SUPPORT_TOKENS:
            text += f"{token}: {str(getcourcebydior(cfg.SUPPORT_TOKENS[token])).replace(',', '.')}\n"
        with open('utils/.txt/cource.txt', 'w') as f:
            f.write(text.replace(',', '.'))
        sleep(45)

def readcource():
    tokens = {}
    with open("utils/.txt/cource.txt", 'r') as f:
        for line in f.readlines():
            if line.split(':')[0] in cfg.SUPPORT_TOKENS:
                tokens[line.split(':')[0]] = line.split(' ')[1].replace('\n', '').replace(',', '.')
    return tokens
