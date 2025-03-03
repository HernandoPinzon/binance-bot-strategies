import pandas as pd
from utils.ccxt_client import exchange
from utils.save_data import save_order
from utils.trading_helpers import calculate_ema, get_min_notional, get_min_trade_size
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


def check_signals(queue):
    """Verifica señales de compra o venta usando los datos de la cola"""
    global first_run
    if queue.empty():
        return None
    df = queue.get()

    df["EMA_10"] = calculate_ema(df, EMA_SHORT_PERIOD)
    df["EMA_50"] = calculate_ema(df, EMA_LONG_PERIOD)
    df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
    df["time"] = df["timestamp"].dt.strftime("%H:%M:%S")

    last_row = df.iloc[-1]
    prev_row = df.iloc[-2]

    # Calcular diferencia porcentual con respecto al precio
    ema_diff_percentage = (
        (last_row["EMA_10"] - last_row["EMA_50"]) / last_row["close"]
    ) * 100
    print(f"{last_row['time']} EMA: {ema_diff_percentage:.2f}%")

    # 🚀 Primera vez: Comprar o vender según la tendencia actual
    if first_run:
        first_run = False  # Desactivar la bandera después de la primera ejecución
        if last_row["EMA_10"] > last_row["EMA_50"]:
            print("📌 Primera ejecución: Se detecta tendencia alcista → COMPRA")
            return OrderTypes.BUY
        else:
            print("📌 Primera ejecución: Se detecta tendencia bajista → VENTA")
            return OrderTypes.SELL

    if (
        prev_row["EMA_10"] < prev_row["EMA_50"]
        and last_row["EMA_10"] > last_row["EMA_50"]
    ):
        print("Señal de COMPRA detectada (EMA_10 cruzó hacia arriba EMA_50)")
        return OrderTypes.BUY

    if (
        prev_row["EMA_10"] > prev_row["EMA_50"]
        and last_row["EMA_10"] < last_row["EMA_50"]
    ):
        print("Señal de VENTA detectada (EMA_10 cruzó hacia abajo EMA_50)")
        return "SELL"
    return "HOLD"


def place_order(order_type, client):
    try:
        if not hasattr(place_order, "last_sell_price"):
            place_order.last_sell_price = 0  # Inicializar con 0 o un valor adecuado
        if not hasattr(place_order, "last_buy_price"):
            place_order.last_buy_price = 0  # Inicializar con 0 o un valor adecuado

        min_trade_size = get_min_trade_size(SYMBOL.value, client)
        account_info = client.get_account()
        balance_c1 = next(
            asset for asset in account_info["balances"] if asset["asset"] == "LTC"
        )["free"]
        balance_c2 = next(
            asset for asset in account_info["balances"] if asset["asset"] == "USDT"
        )["free"]
        ticker = client.get_symbol_ticker(symbol=SYMBOL.value)
        current_price = float(ticker["price"])
        quantity = TRADE_AMOUNT_USDT / current_price
        quantity = round(quantity - (quantity % min_trade_size), 6)
        print(
            f"🔹 Enviando orden: {order_type} - Símbolo: {SYMBOL.value} - Cantidad: {quantity} - Balance: {balance_c1}"
        )
        order = client.create_order(
            symbol=SYMBOL.value,
            side=order_type,
            type="MARKET",
            quantity=quantity,
        )

        # Extraer información de la orden
        executed_price = float(order["fills"][0]["price"])  # Precio real de ejecución
        fee = sum(float(f["commission"]) for f in order["fills"])  # Comisiones totales
        if fee == 0:
            fee = 0.001 * executed_price * quantity

        profit_loss = 0
        if order_type == OrderTypes.BUY:
            profit_loss = (place_order.last_sell_price - executed_price) * quantity
            place_order.last_buy_price = executed_price  # Guardamos precio de compra
            print("🟢 ORDEN DE COMPRA:", order)
        elif order_type == OrderTypes.SELL:
            place_order.last_sell_price = executed_price  # Guardamos precio de compra
            profit_loss = (executed_price - place_order.last_buy_price) * quantity
            print("🔴 ORDEN DE VENTA:", order)
        else:
            profit_loss = 0
        save_order(
            order_type=order_type,
            price=executed_price,
            quantity=quantity,
            fee=fee,
            profit_loss=profit_loss,
            balance_c1=balance_c1,
            balance_c2=balance_c2,
            ema_short=EMA_SHORT_PERIOD,  # Guardamos el periodo configurado (ej. 10)
            ema_long=EMA_LONG_PERIOD,  # Guardamos el periodo configurado (ej. 50)
            interval=INTERVAL.value,  # Guardamos el intervalo configurado (ej. 1m)
        )
    except Exception as e:
        print(f"❌ ERROR AL EJECUTAR ORDEN: {e}")
