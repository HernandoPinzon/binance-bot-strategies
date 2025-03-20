import os
from config import LEVERAGE, SYMBOL
from future_utils.adjust_tick_price import adjust_tick_price
from dotenv import load_dotenv
from binance.client import Client
import state

from utils.generate_csv_name import generate_csv_name_with_config

load_dotenv()
state.csv_file_name = generate_csv_name_with_config("real_buy")
API_KEY = os.getenv("BINANCE_REAL_API_KEY")
API_SECRET = os.getenv("BINANCE_REAL_API_SECRET")
client = Client(API_KEY, API_SECRET)

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
take_profit_percentage = 0.003
stop_loss_percentage = 0.002
print(f"✅ Rango permitido: {min_price:.2f} - {max_price:.2f}")

# Ajustar el precio de entrada ligeramente dentro del rango permitido
QUANTITY = 0.3  # Tamaño de la orden
ORDER_SIDE = "SELL"  # Lado de la orden


# 1️⃣ Establecer el apalancamiento
client.futures_change_leverage(symbol=SYMBOL.value, leverage=LEVERAGE)
#client.futures_change_margin_type(symbol=SYMBOL.value, marginType="ISOLATED")


ticker = client.futures_symbol_ticker(symbol=SYMBOL.value)
last_price = float(ticker["price"])

entry_price = adjust_tick_price(last_price, tick_size)
if ORDER_SIDE == "BUY":
    TAKE_PROFIT = entry_price * (1 + take_profit_percentage)
    STOP_LOSS = entry_price * (1 - stop_loss_percentage)
else:
    TAKE_PROFIT = entry_price * (1 - take_profit_percentage)
    STOP_LOSS = entry_price * (1 + stop_loss_percentage)
STOP_LOSS = adjust_tick_price(STOP_LOSS, tick_size)
TAKE_PROFIT = adjust_tick_price(TAKE_PROFIT, tick_size)

# 2️⃣ Abrir una orden de compra en mercado
print(f"🔵 Precio de entrada: {entry_price} Cantidad: {QUANTITY}")

client.futures_create_order(
    symbol=SYMBOL.value,
    side=ORDER_SIDE,
    type="LIMIT",
    timeInForce="GTC",
    price=str(entry_price),
    quantity=QUANTITY,
)

# 4️⃣ Colocar el Stop Loss (SL)
""" print(f"🔴 Precio de Stop Loss: {STOP_LOSS} Cantidad: {QUANTITY}")
client.futures_create_order(
    symbol=SYMBOL.value,
    side="SELL" if ORDER_SIDE == "BUY" else "BUY",
    type="STOP_MARKET",
    stopPrice=str(STOP_LOSS),
    quantity=QUANTITY,  # Se cierra solo esta orden
    reduceOnly=True,  # Evita cerrar toda la posición
    newClientOrderId=f"SL-{order_id}",  # ID único para seguimiento
)

print(f"🟢 Precio de Take Profit: {TAKE_PROFIT} Cantidad: {QUANTITY}")
client.futures_create_order(
    symbol=SYMBOL.value,
    side="SELL" if ORDER_SIDE == "BUY" else "BUY",
    type="TAKE_PROFIT_MARKET",
    stopPrice=str(TAKE_PROFIT),
    quantity=QUANTITY,  # Se cierra solo esta orden
    reduceOnly=True,  # Evita cerrar toda la posición
    newClientOrderId=f"TP-{order_id}",  # ID único para seguimiento
)

print(f"✅ Orden abierta en {entry_price} con SL en {STOP_LOSS} y TP en {TAKE_PROFIT}")
 """