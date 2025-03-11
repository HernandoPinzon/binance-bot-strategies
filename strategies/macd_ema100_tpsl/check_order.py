import state
import strategies.macd_ema100_tpsl.strategy_state as strategy_state
from strategies.macd_ema100_tpsl.utils.save_data import save_order
from config import SYMBOL, INTERVAL
from strategies.macd_ema100_tpsl.strategy_config import (
    STOP_LOSS_PERCENT,
    TAKE_PROFIT_PERCENT,
)

# Lista de órdenes abiertas
strategy_state.open_orders = []


def place_order(order_type, candle, next_candle):
    """Coloca una orden y define los niveles de SL y TP en base al porcentaje."""

    price_entry = candle["close"]
    stop_loss = (
        price_entry * (1 - STOP_LOSS_PERCENT / 100)
        if order_type == "BUY"
        else price_entry * (1 + STOP_LOSS_PERCENT / 100)
    )
    take_profit = (
        price_entry * (1 + TAKE_PROFIT_PERCENT / 100)
        if order_type == "BUY"
        else price_entry * (1 - TAKE_PROFIT_PERCENT / 100)
    )

    order = {
        "order_type": order_type,
        "price_entry": price_entry,
        "stop_loss": stop_loss,
        "take_profit": take_profit,
        "entry_time": next_candle["timestamp"],
    }

    strategy_state.open_orders.append(order)


def check_orders(candle):
    """Revisa si alguna orden alcanzó el SL o TP y la cierra."""
    closed_orders = []

    for order in strategy_state.open_orders:
        if order["order_type"] == "BUY":
            if candle["low"] <= order["stop_loss"]:
                closed_orders.append((order, "SL", candle["timestamp"]))
            elif candle["high"] >= order["take_profit"]:
                closed_orders.append((order, "TP", candle["timestamp"]))

        elif order["order_type"] == "SELL":
            if candle["high"] >= order["stop_loss"]:
                closed_orders.append((order, "SL", candle["timestamp"]))
            elif candle["low"] <= order["take_profit"]:
                closed_orders.append((order, "TP", candle["timestamp"]))

    # Eliminar órdenes cerradas y guardarlas en el CSV
    for order, reason, exit_time in closed_orders:
        save_order(
            transact_time=order["entry_time"].strftime(
                "%Y-%m-%d %H:%M:%S"
            ),  # Guardamos la entrada
            exit_time=exit_time.strftime("%Y-%m-%d %H:%M:%S"),  # Guardamos la salida
            order_type=order["order_type"],
            price_order=order["price_entry"],
            interval=INTERVAL.value,
            symbol=SYMBOL.value,
            csv_filename=state.csv_file_name,
            exit_reason=reason,
        )
        strategy_state.open_orders.remove(order)
