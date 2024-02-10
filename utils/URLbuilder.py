from bot import config

def buildurl(id: str):
    return f"ton://transfer/{config.DEPOSIT_ADDRESS}?jetton=EQDf84FT8tdHZeI2-LXdb8gPMRqHRSABrmi8jI7MzvVpGJKZ&fee-amount=0.1&allow_custom=1&text={id}"

def buildurlfordeal(com: str):
    return f"ton://transfer/{config.DEPOSIT_ADDRESS}?text={com}&amount={int(config.MARKET_DEAL_PRICE*1000000000)}"


