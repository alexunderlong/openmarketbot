import asyncio
import logging
import multiprocessing
import sys
import utils.getcourcebydior
from bot import main
from dbs import dealsdb
from utils import tondep


def tond():
    asyncio.run(tondep.start())


def mainstart():
    asyncio.run(main.main())


def cource():
    utils.getcourcebydior.whritecource()


def check_time():
    asyncio.run(dealsdb.check_deal_time())



if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    p1 = multiprocessing.Process(target=cource)
    p2 = multiprocessing.Process(target=mainstart)
    p3 = multiprocessing.Process(target=tond)
    p4 = multiprocessing.Process(target=check_time)
    p1.start()
    p2.start()
    p3.start()
    p4.start()
    print('ALL MODULES STARTED')
