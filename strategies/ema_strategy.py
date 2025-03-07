import pandas as pd
from utils.save_data import save_order
from utils.trading_helpers import calculate_ema
from config import (
    OrderTypes,
    SYMBOL,
    INTERVAL,
    TRADE_AMOUNT_USDT,
    EMA_SHORT_PERIOD,
    EMA_LONG_PERIOD,
)
import time
import datetime

first_run = True
previous_ema_diff_percentage = None


def check_signals(queue):
    """Verifica señales de compra o venta usando los datos de la cola"""
    global first_run, previous_ema_diff_percentage
    if queue.empty():
        return None
    df = queue.get()

    df["EMA_10"] = calculate_ema(df, EMA_SHORT_PERIOD)
    df["EMA_50"] = calculate_ema(df, EMA_LONG_PERIOD)
    df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
    df["time"] = df["timestamp"].dt.strftime("%H:%M:%S")

    last_row = df.iloc[-1]
    prev_row = df.iloc[-2]

    ema_diff_percentage = (
        (last_row["EMA_10"] - last_row["EMA_50"]) / last_row["close"]
    ) * 100
    ema_diff_percentage_last = (
        (prev_row["EMA_10"] - prev_row["EMA_50"]) / prev_row["close"]
    ) * 100
    if ema_diff_percentage != previous_ema_diff_percentage:
        if ema_diff_percentage > ema_diff_percentage_last:
            print(f"EMA: 🟢{ema_diff_percentage:.2f}%")
        else:
            print(f"EMA: 🔴{ema_diff_percentage:.2f}%")
        previous_ema_diff_percentage = ema_diff_percentage
    if first_run:
        first_run = False
        if last_row["EMA_10"] > last_row["EMA_50"]:
            return OrderTypes.BUY, last_row["close"]
        else:
            return OrderTypes.SELL, last_row["close"]
    if (
        prev_row["EMA_10"] < prev_row["EMA_50"]
        and last_row["EMA_10"] > last_row["EMA_50"]
    ):
        print("Señal de COMPRA detectada (EMA_10 cruzó hacia arriba EMA_50)")
        return OrderTypes.BUY, last_row["close"]

    if (
        prev_row["EMA_10"] > prev_row["EMA_50"]
        and last_row["EMA_10"] < last_row["EMA_50"]
    ):
        print("Señal de VENTA detectada (EMA_10 cruzó hacia abajo EMA_50)")
        return "SELL", last_row["close"]
    return "HOLD", last_row["close"]

# en el tintero lo de agregar un stop loss
def place_order(order_type, client, min_trade_size, current_price):
    current_time = datetime.datetime.now().strftime("%M:%S")
    print(f"🔹INIT {current_time}")
    try:
        quantity = TRADE_AMOUNT_USDT / current_price
        quantity = round(quantity - (quantity % min_trade_size), 6)
        current_time = datetime.datetime.now().strftime("%M:%S")
        print(f"🔹{current_time} {order_type} CurrentPrice: {current_price}")
        order = client.create_order(
            symbol=SYMBOL.value,
            side=order_type,
            type="MARKET",
            quantity=quantity,
        )
        # Extraer y formatear transactTime
        transact_time = order["transactTime"]
        transact_time_formatted = datetime.datetime.fromtimestamp(
            transact_time / 1000
        ).strftime("%H:%M:%S")

        # Extraer información de la orden
        executed_price = float(order["fills"][0]["price"])  # Precio real de ejecución
        print(f"🔹{executed_price}")
        save_order(
            transact_time=transact_time_formatted,
            order_type=order_type,
            price_on_order=current_price,
            price=executed_price,
            quantity=quantity,
            ema_short=EMA_SHORT_PERIOD,
            ema_long=EMA_LONG_PERIOD,
            interval=INTERVAL.value,
            symbol=SYMBOL.value,
            csv_file="trading_historyV4.csv",
        )
    except Exception as e:
        print(f"❌ ERROR AL EJECUTAR ORDEN: {e}")
