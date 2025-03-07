from utils.save_data import save_order
from config import (
    SYMBOL,
    INTERVAL,
    EMA_SHORT_PERIOD,
    EMA_LONG_PERIOD,
)
import datetime

previous_price = None


def place_order(order_type, candle, next_candle, csv_name):
    global previous_price
    transact_time = next_candle["timestamp"].strftime("%Y-%m-%d %H:%M:%S")
    final_price = None
    if previous_price is not None:
        # mitigación de riesgos, tal vez ponerle un poco mas de margen de perdida para asegurar que entre
        if order_type == "BUY":
            if previous_price < candle["close"]:
                final_price = candle["close"]
        else:
            if previous_price > candle["close"]:
                final_price = candle["close"]
        if final_price is not None:
            previous_price = final_price
            if order_type == "BUY":
                order_type = "SELL"
            else:
                order_type = "BUY"
            save_order(
                transact_time=transact_time,
                order_type=order_type,
                price_order=candle["close"],
                price_final=final_price,
                quantity="STOP_LOSS",
                ema_short=EMA_SHORT_PERIOD,
                ema_long=EMA_LONG_PERIOD,
                interval=INTERVAL.value,
                symbol=SYMBOL.value,
                csv_file=csv_name,
            )

    # mini take a bit more profit
    if (order_type == "BUY" and next_candle["low"] < candle["low"]) or (
        order_type == "SELL" and next_candle["high"] > candle["high"]
    ):
        if order_type == "BUY":
            final_price = candle["low"]
        else:
            final_price = candle["high"]
        previous_price = final_price
        if order_type == "BUY":
            order_type = "SELL"
        else:
            order_type = "BUY"
        save_order(
            transact_time=transact_time,
            order_type=order_type,
            price_order=candle["close"],
            price_final=final_price,
            quantity="TAKE_BIT_PROFIT",
            ema_short=EMA_SHORT_PERIOD,
            ema_long=EMA_LONG_PERIOD,
            interval=INTERVAL.value,
            symbol=SYMBOL.value,
            csv_file=csv_name,
        )
