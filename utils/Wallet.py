from TonTools.Providers.TonCenterClient import TonCenterClient

from bot import config

client = TonCenterClient(config.TONCENTER_API_KEY)
source_wallet_mnemonic = config.DEPOSIT_ADDRESS_MNEMONIC
jetton_master_address = config.OPEN_MASTER_ADDRESS

my_wallet = Wallet(provider=client, mnemonics=source_wallet_mnemonic, version='v4r2')

async def transfer(destination_wallet: str, amount: float):
    if len(destination_wallet) == 48:
        await my_wallet.transfer_jetton(destination_address=destination_wallet,
                                        jetton_master_address=jetton_master_address,
                                        jettons_amount=amount, fee=0.05)
        return True
    elif destination_wallet.endswith('.ton') or destination_wallet.endswith('.t.me'):
        destination_wallet = await getaddrbydns(destination_wallet)
        if len(str(destination_wallet)) == 48:
            await my_wallet.transfer_jetton(destination_address=destination_wallet,
                                            jetton_master_address=jetton_master_address,
                                            jettons_amount=amount, fee=0.05)
            return True
        else:
            return False
    else:
        return False
