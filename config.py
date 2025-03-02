# config.py

from enum import Enum

class SYMBOLS(Enum):
    BTC_USDT = "BTC/USDT"
    ETH_USDT = "ETH/USDT"
    BNB_USDT = "BNB/USDT"
    LTC_USDT = "LTC/USDT"

class INTERVALS(Enum):
    M1 = "1m"
    M5 = "5m"
    H1 = "1h"
    D1 = "1d"

# Parámetros de la estrategia
SYMBOL = SYMBOLS.LTC_USDT
INTERVAL = INTERVALS.M1
QUANTITY = 0.001 # Cantidad a operar
EMA_SHORT_PERIOD = 10
EMA_LONG_PERIOD = 50
