import os
from config import SYMBOL
from future_utils.adjust_tick_price import adjust_tick_price
from dotenv import load_dotenv
from binance.client import Client
import state

from utils.generate_csv_name import generate_csv_name_with_config

load_dotenv()
state.csv_file_name = generate_csv_name_with_config("live_random_buy_sell")
API_KEY = os.getenv("BINANCE_FUTURE_API_KEY")
API_SECRET = os.getenv("BINANCE_FUTURE_API_SECRET")
client = Client(API_KEY, API_SECRET, testnet=True)

info = client.futures_exchange_info()
for symbol_info in info["symbols"]:
    if symbol_info["symbol"] == SYMBOL.value:
        tick_size = float(symbol_info["filters"][0]["tickSize"])
        print(f"🔹 Tick Size para {SYMBOL.value}: {tick_size}")

ticker = client.futures_symbol_ticker(symbol=SYMBOL.value)
last_price = float(ticker["price"])
print(f"🔹 Último precio de BTCUSDT: {last_price}")
max_price = last_price * 1.10  # 110% del precio actual
min_price = last_price * 0.90  # 90% del precio actual
print(f"✅ Rango permitido: {min_price:.2f} - {max_price:.2f}")


ticker = client.futures_symbol_ticker(symbol=SYMBOL.value)
last_price = float(ticker["price"])

# Ajustar el precio de entrada ligeramente dentro del rango permitido
QUANTITY = 0.1  # Tamaño de la orden
LEVERAGE = 10  # Apalancamiento
ORDER_SIDE = "BUY"  # Lado de la orden


# 1️⃣ Establecer el apalancamiento
client.futures_change_leverage(symbol=SYMBOL.value, leverage=LEVERAGE)


ticker = client.futures_symbol_ticker(symbol=SYMBOL.value)
last_price = float(ticker["price"])

entry_price = adjust_tick_price(last_price, tick_size)
STOP_LOSS = entry_price * 0.995
TAKE_PROFIT = entry_price * 1.005
STOP_LOSS = adjust_tick_price(STOP_LOSS, tick_size)
TAKE_PROFIT = adjust_tick_price(TAKE_PROFIT, tick_size)

# 2️⃣ Abrir una orden de compra en mercado
print(f"🔵 Precio de entrada: {entry_price} Cantidad: {QUANTITY}")
order = client.futures_create_order(
    symbol=SYMBOL.value,
    side=ORDER_SIDE,
    type="LIMIT",
    timeInForce="GTC",
    price=str(entry_price),
    quantity=QUANTITY,
)
order_id = order["orderId"]

# 3️⃣ Obtener el precio real de entrada
entry_price = float(
    client.futures_position_information(symbol=SYMBOL.value)[0]["entryPrice"]
)
print(client.futures_position_information(symbol=SYMBOL.value))


# 4️⃣ Colocar el Stop Loss (SL)
print(f"🔴 Precio de Stop Loss: {STOP_LOSS} Cantidad: {QUANTITY}")
client.futures_create_order(
    symbol=SYMBOL.value,
    side="SELL",
    type="STOP_MARKET",
    stopPrice=str(STOP_LOSS),
    quantity=QUANTITY,  # Se cierra solo esta orden
    reduceOnly=True,  # Evita cerrar toda la posición
    newClientOrderId=f"SL-{order_id}",  # ID único para seguimiento
)

print(f"🟢 Precio de Take Profit: {TAKE_PROFIT} Cantidad: {QUANTITY}")
client.futures_create_order(
    symbol=SYMBOL.value,
    side="SELL",
    type="TAKE_PROFIT_MARKET",
    stopPrice=str(TAKE_PROFIT),
    quantity=QUANTITY,  # Se cierra solo esta orden
    reduceOnly=True,  # Evita cerrar toda la posición
    newClientOrderId=f"TP-{order_id}",  # ID único para seguimiento
)

print(f"✅ Orden abierta en {entry_price} con SL en {STOP_LOSS} y TP en {TAKE_PROFIT}")
