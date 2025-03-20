# state.py
import time
import requests
from datetime import datetime, timezone
from binance.exceptions import BinanceAPIException
from config import COIN_NAMES, EMA_LONG_PERIOD, EMA_SHORT_PERIOD, INTERVAL, SYMBOL
from utils.save_data import save_order
from utils.trading_helpers import adjust_quantity


balance_coin_1 = 0.0
balance_coin_USDT = 0.0
min_trade_size = None
max_trade_size = None
step_size = 0.001  # Un valor por defecto válido
previous_price_execute = None
client = None
last_signal = None
init_price = 0.0
csv_file_name = "template"
min_notional = 0.0
tick_size = 0.0
capital_usdt = 1000
trades = []
order_size = 0.01
strategy = "macd"


def update_balance(order_type, quantity, price):
    global balance_coin_1, balance_coin_USDT
    quantity = float(quantity)
    price = float(price)
    if order_type == "BUY":
        balance_coin_1 += quantity
        balance_coin_USDT -= quantity * price
    else:
        balance_coin_1 -= quantity
        balance_coin_USDT += quantity * price
    print(f"Balance de {COIN_NAMES[0]}: {balance_coin_1}")
    print(f"Balance de {COIN_NAMES[1]}: {balance_coin_USDT}")


def verify_or_cancel_limit_order(limit_order, time_end, signal):
    global client, previous_price_execute, last_signal, csv_file_name
    if client is None or limit_order is None:
        return
    order_start_time = time.time()
    canceled_or_filled = False
    attempts = 0
    max_attempts = 62
    while canceled_or_filled is False and attempts < max_attempts:
        attempts += 1
        elapsed_time = time.time() - order_start_time
        if elapsed_time < time_end:
            try:
                order_status = client.get_order(
                    symbol=SYMBOL.value, orderId=limit_order["orderId"]
                )
                if order_status["status"] == "FILLED":
                    executed_price = float(order_status["price"])
                    update_balance(signal, limit_order["origQty"], executed_price)
                    execution_time = datetime.fromtimestamp(
                        order_status["updateTime"] / 1000, tz=timezone.utc
                    )
                    save_order(
                        transact_time=execution_time.strftime("%Y-%m-%d %H:%M:%S UTC"),
                        order_type=signal,
                        price_order="WAS LIMIT: NA",
                        price_final=executed_price,
                        quantity="TAKE_BIT_PROFIT",
                        ema_short=EMA_SHORT_PERIOD,
                        ema_long=EMA_LONG_PERIOD,
                        interval=INTERVAL.value,
                        symbol=SYMBOL.value,
                        csv_filename=csv_file_name,
                    )
                    previous_price_execute = executed_price
                    last_signal = signal
                    canceled_or_filled = True
            except Exception as e:
                print(f"Error al obtener orden: {e}")
        else:
            try:
                # cancelar orden
                client.cancel_order(symbol=SYMBOL.value, orderId=limit_order["orderId"])
                canceled_or_filled = True
                if last_signal == "BUY":
                    last_signal = "SELL"
                else:
                    last_signal = "BUY"
            except Exception as e:
                print(f"Error al cancelar orden: {e}")
        time.sleep(1)


def adjust_balance():
    global balance_coin_1, balance_coin_USDT, client, init_price, min_notional
    if client is None:
        return
    if init_price is None:
        return
    print("Ajustando balance")
    balance_coin_1 = float(balance_coin_1)
    balance_coin_USDT = float(balance_coin_USDT)
    try:
        if balance_coin_1 * init_price < min_notional:
            buy_amount = adjust_quantity(balance_coin_USDT / init_price / 2, step_size)
            print(f"AJUSTANDO con compra de {buy_amount}")
            order = client.create_order(
                symbol=SYMBOL.value,
                side="BUY",
                type="MARKET",
                quantity=buy_amount,
            )
            update_balance("BUY", order["executedQty"], order["fills"][0]["price"])
        if balance_coin_USDT < min_notional:
            print(f"AJUSTANDO con venta de {balance_coin_1 / 2}")
            order = client.create_order(
                symbol=SYMBOL.value,
                side="SELL",
                type="MARKET",
                quantity=adjust_quantity(balance_coin_1 / 2, step_size),
            )
            update_balance("SELL", order["executedQty"], order["fills"][0]["price"])

    except Exception as e:
        print(f"Error al ajustar balance: {e}")


def update_balance2():
    global balance_coin_1, balance_coin_USDT, client
    if client is None:
        return
    coin_1 = client.get_asset_balance(asset=COIN_NAMES[0])
    coin_2 = client.get_asset_balance(asset=COIN_NAMES[1])
    if coin_1 is not None and coin_2 is not None:
        balance_coin_1 = float(coin_1["free"])
        balance_coin_USDT = float(coin_2["free"])
        print(f"Balance de {COIN_NAMES[0]}: {balance_coin_1}")
        print(f"Balance de {COIN_NAMES[1]}: {balance_coin_USDT}")


def update_balance3():
    global balance_coin_USDT, client
    if client is None:
        return
    try:
        account_balance = client.futures_account_balance()
        for coin in account_balance:
            if coin["asset"] == COIN_NAMES[1]:
                balance_coin_USDT = float(coin["balance"])
        print(f"Balance de {COIN_NAMES[1]}: {balance_coin_USDT}")
    except requests.exceptions.ReadTimeout:
        print("⏳ Tiempo de espera agotado. Reintentando en 5 segundos...") # Reintenta la solicitud
    except BinanceAPIException as e:
        print(f"❌ Error en la API de Binance: {e}")
        return None
