from utils.getAddrByDns import getaddrbydns
from TonTools.Contracts.Wallet import Wallet
from TonTools.Providers.TonCenterClient import TonCenterClient
from bot import config

client = TonCenterClient(config.TONCENTER_API_KEY)
source_wallets_mnemonic = config.SHARDS_MNEMONIC


shard0 = Wallet(provider=client, mnemonics=source_wallets_mnemonic[0], version='v4r2')
shard1 = Wallet(provider=client, mnemonics=source_wallets_mnemonic[1], version='v4r2')
shard2 = Wallet(provider=client, mnemonics=source_wallets_mnemonic[2], version='v4r2')
shard3 = Wallet(provider=client, mnemonics=source_wallets_mnemonic[3], version='v4r2')
shards = [shard0, shard1, shard2, shard3]


async def transfer(destination_wallet: str, amount: float, token: str, shardid: int):
    shard = shards[shardid]
    if len(destination_wallet) == 48:
        await shard.transfer_jetton(destination_address=destination_wallet,
                                     jetton_master_address=config.SUPPORT_TOKENS[token],
                                     jettons_amount=amount)
        return True
    elif destination_wallet.endswith('.ton') or destination_wallet.endswith('.t.me'):
        destination_wallet = await getaddrbydns(destination_wallet)
        if len(str(destination_wallet)) == 48:
            await shard.transfer_jetton(destination_address=destination_wallet,
                                        jetton_master_address=config.SUPPORT_TOKENS[token],
                                        jettons_amount=amount)
            return True
        else:
            return False
    else:
        return False


async def tontransfer(destination_wallet: str, amount: float, shardid: int):
    wallet = shards[shardid]
    if len(destination_wallet) == 48:
        await wallet.transfer_ton(destination_address=destination_wallet,
                                  amount=amount)
        return True
    elif destination_wallet.endswith('.ton') or destination_wallet.endswith('.t.me'):
        destination_wallet = await getaddrbydns(destination_wallet)
        if len(str(destination_wallet)) == 48:
            await wallet.transfer_ton(destination_address=destination_wallet,
                                      amount=amount)
            return True
        else:
            return False
    else:
        return False
