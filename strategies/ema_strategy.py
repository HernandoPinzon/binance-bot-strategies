import pandas as pd
from utils.ccxt_client import exchange
from utils.save_data import save_order
from utils.trading_helpers import calculate_ema, get_min_notional
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


def check_signals(queue):
    """Verifica señales de compra o venta usando los datos de la cola"""
    if queue.empty():
        return None  # Si no hay datos, no hacer nada

    df = queue.get()  # Obtener los datos más recientes

    df["EMA_10"] = calculate_ema(df, EMA_SHORT_PERIOD)
    df["EMA_50"] = calculate_ema(df, EMA_LONG_PERIOD)

    df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")  # Convertir timestamp
    df["time"] = df["timestamp"].dt.strftime("%H:%M:%S")  # Crear la columna 'time'

    last_row = df.iloc[-1]
    prev_row = df.iloc[-2]  # Fila anterior para comparar cruce

    # Calcular diferencia porcentual con respecto al precio
    ema_diff_percentage = (
        (last_row["EMA_10"] - last_row["EMA_50"]) / last_row["close"]
    ) * 100

    print(f"{last_row['time']} EMA: {ema_diff_percentage:.2f}%")

    # Agregar impresión con time actual
    """ now = datetime.datetime.now().strftime("%H:%M:%S")

    print(
        f"REAL_TIME: {now} - MARKET_TIME: {last_row['time']} - Precio: {last_row['close']} - EMA_10: {last_row['EMA_10']:.2f} - EMA_50: {last_row['EMA_50']:.2f}"
    ) """

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

        ticker = client.get_symbol_ticker(SYMBOL.value)
        current_price = float(ticker["last"])  # Último precio del activo
        if order_type == OrderTypes.BUY:
            quantity = TRADE_AMOUNT_USDT / current_price  # Cantidad en BTC a comprar
        elif order_type == OrderTypes.SELL:
            quantity = TRADE_AMOUNT_USDT / current_price  # Cantidad en BTC a vender
        else:
            print("⚠️ Tipo de orden no reconocido")
            return
        quantity = round(quantity, 6)
        print(
            f"🔹 Enviando orden: {order_type} - Símbolo: {SYMBOL.value} - Cantidad: {quantity}"
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
        balance = client.fetch_balance()["total"]["USDT"]  # Saldo total en USDT

        if order_type == OrderTypes.BUY:
            place_order.last_buy_price = executed_price  # Guardamos precio de compra
            print("🟢 ORDEN DE COMPRA:", order)
        elif order_type == OrderTypes.SELL:
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
            balance=balance,
            ema_short=EMA_SHORT_PERIOD,  # Guardamos el periodo configurado (ej. 10)
            ema_long=EMA_LONG_PERIOD,  # Guardamos el periodo configurado (ej. 50)
            interval=INTERVAL.value,  # Guardamos el intervalo configurado (ej. 1m)
        )
    except Exception as e:
        print(f"❌ ERROR AL EJECUTAR ORDEN: {e}")
