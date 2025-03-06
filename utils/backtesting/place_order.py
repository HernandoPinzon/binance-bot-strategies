from utils.save_data import save_order
from config import (
    SYMBOL,
    INTERVAL,
    EMA_SHORT_PERIOD,
    EMA_LONG_PERIOD,
)
import datetime


# TODO: Implementar el traerme las ordenes verdaderas y no solo la vela para validar el precio de compra
def place_order(order_type, candle, next_candle):
    transact_time = candle["timestamp"].strftime("%Y-%m-%d %H:%M:%S")
    save_order(
        transact_time=transact_time,
        order_type=order_type,
        price_order=candle["close"],
        price_final=next_candle["close"],
        quantity="1",
        ema_short=EMA_SHORT_PERIOD,
        ema_long=EMA_LONG_PERIOD,
        interval=INTERVAL.value,
        symbol=SYMBOL.value,
        csv_file="trading_backtesting.csv",
    )
