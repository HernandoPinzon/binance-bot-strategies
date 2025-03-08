import asyncio
import datetime

from config import EMA_LONG_PERIOD, EMA_SHORT_PERIOD, INTERVAL, SYMBOL, TRADE_AMOUNT_USDT
from utils.save_data import save_order

#Cancelar todas las órdenes abiertas antes de la siguiente
def place_order_inverse(order_type, client, min_trade_size, current_price):
    global previous_price
    current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    quantity = TRADE_AMOUNT_USDT / current_price
    quantity = round(quantity - (quantity % min_trade_size), 6)

    try:
        # Crear orden límite con expiración en 1 minuto
        order = client.create_order(
            symbol=SYMBOL.value,
            side=order_type,
            type="LIMIT",
            timeInForce="GTC",  # Cambiar a "GTC" si no se admite "FOK"
            quantity=quantity,
            price=current_price,
        )
        print(f"🔹{current_time} {order_type} LIMIT order placed at {current_price}")

        # Esperar 1 minuto antes de verificar si la orden se ejecutó
        asyncio.run(asyncio.sleep(60))

        # Revisar si la orden se ejecutó
        order_status = client.get_order(orderId=order["orderId"], symbol=SYMBOL.value)
        if order_status["status"] == "FILLED":
            executed_price = float(order_status["price"])
            previous_price = executed_price  # Actualizar precio previo
            print(f"✅ Orden ejecutada a {executed_price}")
        else:
            print(f"❌ Orden límite no ejecutada en 1 min, cancelando...")
            client.cancel_order(orderId=order["orderId"], symbol=SYMBOL.value)
            return

        # Decidir el tipo de orden siguiente
        if order_type == "BUY":
            stop_loss_price = executed_price * 0.99  # Stop loss al 1%
            order_type = "SELL"
        else:
            stop_loss_price = executed_price * 1.01  # Stop loss al 1%
            order_type = "BUY"

        # Colocar orden de Stop Loss de tipo MARKET
        client.create_order(
            symbol=SYMBOL.value,
            side=order_type,
            type="MARKET",
            quantity=quantity,
        )
        print(f"🔹 Stop Loss ejecutado a {stop_loss_price}")

        # Guardar datos en CSV
        save_order(
            transact_time=current_time,
            order_type=order_type,
            price_order=current_price,
            price_final=executed_price,
            quantity=quantity,
            ema_short=EMA_SHORT_PERIOD,
            ema_long=EMA_LONG_PERIOD,
            interval=INTERVAL.value,
            symbol=SYMBOL.value,
            csv_file="trading_historyV4.csv",
        )
    except Exception as e:
        print(f"❌ ERROR AL EJECUTAR ORDEN: {e}")
