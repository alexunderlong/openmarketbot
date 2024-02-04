import asyncio
import logging
import multiprocessing
import sys
from bot import main
from utils import tondep


def tond():
    asyncio.run(tondep.start())


def mainstart():
    asyncio.run(main.main())


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    p1 = multiprocessing.Process(target=mainstart)
    p2 = multiprocessing.Process(target=tond)
    p1.start()
    p2.start()
