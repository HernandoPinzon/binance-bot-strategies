import state
import strategies.macd_ema100_tpsl.strategy_state as strategy_state
from strategies.macd_ema100_tpsl.utils.save_data import save_order
from config import SYMBOL, INTERVAL
from strategies.macd_ema100_tpsl.strategy_config import (
    STOP_LOSS_PERCENT,
    TAKE_PROFIT_PERCENT,
)

# Diccionario para almacenar órdenes abiertas
strategy_state.open_orders = (
    []
)  # Lista de órdenes activas en backtesting o live trading


def place_order(order_type, candle):
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
        "timestamp": candle["timestamp"],
    }

    strategy_state.open_orders.append(
        order
    )  # Agregar la orden a la lista de órdenes abiertas

    print(
        f"🟢 {order_type} order placed at {price_entry:.2f} | SL: {stop_loss:.2f} | TP: {take_profit:.2f}"
    )


def check_orders(candle):
    """Revisa si alguna orden alcanzó el SL o TP y la cierra."""
    closed_orders = []

    for order in strategy_state.open_orders:
        if order["order_type"] == "BUY":
            if candle["low"] <= order["stop_loss"]:
                closed_orders.append((order, "SL"))
            elif candle["high"] >= order["take_profit"]:
                closed_orders.append((order, "TP"))

        elif order["order_type"] == "SELL":
            if candle["high"] >= order["stop_loss"]:
                closed_orders.append((order, "SL"))
            elif candle["low"] <= order["take_profit"]:
                closed_orders.append((order, "TP"))

    # Eliminar órdenes cerradas y guardarlas en el CSV
    for order, reason in closed_orders:
        save_order(
            transact_time=candle["timestamp"].strftime("%Y-%m-%d %H:%M:%S"),
            order_type=order["order_type"],
            price_order=order["price_entry"],
            interval=INTERVAL.value,
            symbol=SYMBOL.value,
            csv_filename=state.csv_file_name,
            exit_reason=reason,
        )
        strategy_state.open_orders.remove(
            order
        )  # Eliminar la orden de la lista de órdenes abiertas
