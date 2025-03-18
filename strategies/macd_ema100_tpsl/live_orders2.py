import time
from binance.enums import (
    ORDER_TYPE_LIMIT,
    SIDE_BUY,
    SIDE_SELL,
)
import state
from config import LEVERAGE, SYMBOL
from utils.trading_helpers import (
    adjust_quantity_dor_coinUSDT,
)

QUANTITY = 0.3
last_order_candle_time = 0


def place_future_order(order_type, candle):
    global last_order_candle_time
    if last_order_candle_time == candle["timestamp"].strftime("%H:%M"):
        return
    last_order_candle_time = candle["timestamp"].strftime("%H:%M")
    if state.client is None:
        return
    state.update_balance3()
    price = float(candle["close"])
    quantity_usdt = adjust_quantity_dor_coinUSDT(
        state.balance_coin_USDT / 4 * LEVERAGE / price,
        state.step_size,
    )
    print("Cantidad a comprar:", quantity_usdt)
    print(f"{order_type}...")
    state.client.futures_create_order(
        symbol=SYMBOL.value,
        side=SIDE_BUY if order_type == "BUY" else SIDE_SELL,
        type=ORDER_TYPE_LIMIT,
        timeInForce="GTC",
        price=str(price),
        quantity=QUANTITY,
        newClientOrderId=f"{state.strategy}-{SYMBOL.value}-{time.time()}",
    )
    print(f"🟢 order placed at {price:.2f}")
