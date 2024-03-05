import asyncio

from pytonapi import AsyncTonapi
from pytonapi.exceptions import TONAPINotFoundError, TONAPIInternalServerError

from bot import config


async def getaddrbydns(dns: str):
    tonapi = AsyncTonapi(config.TON_API_KEY)
    try:
        raw = (await tonapi.dns.resolve(dns)).wallet.address.to_raw()
        addr = await tonapi.accounts.parse_address(raw)
        return addr.non_bounceable.b64url
    except TONAPINotFoundError:
        return 404
    except TONAPIInternalServerError:
        return 500
