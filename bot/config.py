TOKEN = "YOUR BOT TOKEN"
TON_API_KEY = 'YOUR https://tonapi.io/ API KEY'
TONCENTER_API_KEY = "YOUR https://toncenter.com/ API KEY"
DEPOSIT_ADDRESS_VERSION = 'v4r2'
SUPPORT_TOKENS = {'OPEN': 'EQDf84FT8tdHZeI2-LXdb8gPMRqHRSABrmi8jI7MzvVpGJKZ',
                  'jUSDT': 'EQBynBO23ywHy_CgarY9NK9FTz0yDsG82PtcbSTQgGoXwiuA',
                  'SCALE': 'EQBlqsm144Dq6SjbPI4jjZvA1hqTIP3CvHovbIfW_t-SCALE',
                  'RAFF': 'EQCJbp0kBpPwPoBG-U5C-cWfP_jnksvotGfArPF50Q9Qiv9h',
                  'TONNEL': 'EQDNDv54v_TEU5t26rFykylsdPQsv5nsSZaH_v7JSJPtMitv'}
CHEQUES_FEE = 0.01
SUPPORT_BANKS = ['Тинькофф', 'Сбербанк', 'СБП', 'Альфа-Банк', 'Райффайзен']
RATE_LIMIT = 2
MARKET_DEAL_PRICE = 0.1
MIN_DEAL = 2
SHARDS_MNEMONIC = [['YOUR', 'MNEMONIC', 'PHRASE', 'OF', '1st', 'addr'],
                   ['YOUR', 'MNEMONIC', 'PHRASE', 'OF', '2nd', 'addr'],
                   ['YOUR', 'MNEMONIC', 'PHRASE', 'OF', '3rd', 'addr'],
                   ['YOUR', 'MNEMONIC', 'PHRASE', 'OF', '4th', 'addr']]
SHARDS_ADDRESS = ['1st ton addr',
                  '2nd ton addr',
                  '3rd ton addr',
                  '4th ton addr']
WITHDRAW_FEE = 0.1
RUN_IN_MAINNET = True
SUPPORT_USERNAME = 'OnlineSupportOpenBot'
BOT_ID = 6580078627
#for postgres
DB_NAME = 'db'
DB_USER = 'postgres'
DB_HOST = 'localhost'
DP_PASS = '12345'
#for redis
REDIS_STORAGE_URL = 'redis://localhost:6379/0'


if RUN_IN_MAINNET:
    API_BASE_URL = 'https://toncenter.com'
else:
    API_BASE_URL = 'https://testnet.toncenter.com'
