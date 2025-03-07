# config.py

from enum import Enum
import os


class SYMBOLS(Enum):
    BTC_USDT = "BTCUSDT"
    ETH_USDT = "ETHUSDT"
    BNB_USDT = "BNBUSDT"
    LTC_USDT = "LTCUSDT"


class OrderTypes:
    BUY = "BUY"
    SELL = "SELL"


class INTERVALS(Enum):
    M1 = "1m"
    M5 = "5m"
    H1 = "1h"
    D1 = "1d"
    S1 = "1s"


IntervalsInSeconds = {
    INTERVALS.M1: 60,
    INTERVALS.M5: 300,
    INTERVALS.H1: 3600,
    INTERVALS.D1: 86400,
    INTERVALS.S1: 1,
}


# Parámetros de la estrategia
SYMBOL = SYMBOLS.LTC_USDT
INTERVAL = INTERVALS.M1
TRADE_AMOUNT_USDT = 100  # Cantidad fija en USDT por operación
EMA_SHORT_PERIOD = 10
EMA_LONG_PERIOD = 50

ENABLE_PLOT = False  # Activa o desactiva el gráfico en tiempo real

DB_CONFIG = {
    "name": os.getenv("DB_NAME"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
    "host": os.getenv("DB_HOST"),
    "port": os.getenv("DB_PORT"),
}
