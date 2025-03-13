import datetime
from datetime import datetime, timezone

from config import (
    EMA_LONG_PERIOD,
    EMA_SHORT_PERIOD,
    INTERVAL,
    SYMBOL,
)
from utils.save_data import save_order
import state
from utils.trading_helpers import (
    adjust_quantity_dor_coinUSDT,
    adjust_quantity_for_coin1,
)


# Cancelar todas las órdenes abiertas antes de la siguiente
# Luego de crear la orden verificar el dinero que me queda
def place_order_inverse(
    order_type,
    candle,
):
    print(f"place_order_inverse: {order_type}")
    if state.client is None:
        return
    quantity = None
    final_price = None
    if state.previous_price_execute is not None:
        candle_close_float = float(candle["close"])
        candle_close_float = float(candle["close"])
        if order_type == "BUY":
            if state.previous_price_execute < candle_close_float:
                final_price = candle_close_float
        else:
            if state.previous_price_execute > candle_close_float:
                final_price = candle_close_float
        if final_price is not None:
            if order_type == "BUY":
                order_type = "SELL"
                quantity = adjust_quantity_for_coin1(
                    state.balance_coin_1 * 0.95, state.step_size
                )
            else:
                order_type = "BUY"
                quantity = adjust_quantity_dor_coinUSDT(
                    state.balance_coin_USDT * 0.95 / candle_close_float,
                    state.step_size,
                )
            order = state.client.create_order(
                symbol=SYMBOL.value,
                side=order_type,
                type="MARKET",
                quantity=quantity,
            )
            if order["transactTime"] is None:
                execution_time = datetime.now()
            else:
                execution_time = datetime.fromtimestamp(
                    order["transactTime"] / 1000, tz=timezone.utc
                )
            save_order(
                transact_time=execution_time.strftime("%Y-%m-%d %H:%M:%S"),
                order_type=order_type,
                price_order=candle_close_float,
                price_final=order["fills"][0]["price"],
                quantity=quantity,
                ema_short=EMA_SHORT_PERIOD,
                ema_long=EMA_LONG_PERIOD,
                interval=INTERVAL.value,
                symbol=SYMBOL.value,
                csv_filename=state.csv_file_name,
            )
            state.previous_price_execute = float(order["fills"][0]["price"])
            state.update_balance(order_type, quantity, order["fills"][0]["price"])
    if order_type == "BUY":
        final_price = candle["low"]
        order_type = "SELL"
        print(state.balance_coin_1)
        quantity = adjust_quantity_for_coin1(
            state.balance_coin_1 * 0.95, state.step_size
        )
    else:
        final_price = candle["high"]
        order_type = "BUY"
        print(state.balance_coin_USDT)
        quantity = adjust_quantity_dor_coinUSDT(
            state.balance_coin_USDT * 0.95 / float(candle["close"]), state.step_size
        )
    print(f"{order_type} de {quantity} a {final_price}")
    limit_order = state.client.create_order(
        symbol=SYMBOL.value,
        side=order_type,
        type="LIMIT",
        timeInForce="GTC",
        quantity=quantity,
        price=final_price,
    )
    state.verify_or_cancel_limit_order(limit_order, 59, order_type)
