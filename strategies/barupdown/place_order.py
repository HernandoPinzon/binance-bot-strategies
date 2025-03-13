import state
from strategies.barupdown.save_data import save_order
from config import (
    SYMBOL,
    INTERVAL,
)

previous_price = None


def place_order(order_type, candle, next_candle):
    global previous_price
    transact_time = next_candle["timestamp"].strftime("%Y-%m-%d %H:%M:%S")
    save_order(
        transact_time=transact_time,
        order_type=order_type,
        price_order=candle["close"],
        interval=INTERVAL.value,
        symbol=SYMBOL.value,
        csv_filename=state.csv_file_name,
    )
    return True
