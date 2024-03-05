from bot import config

def buildurl(id: str, masteradr: str, shardid: int):
    return f"ton://transfer/{config.SHARDS_ADDRESS[shardid]}?jetton={masteradr}&allow_custom=1&text={id}"

def buildurlforton(id: str, shardid: int):
    return f"ton://transfer/{config.SHARDS_ADDRESS[shardid]}?text={id}&allow_custom=1"

