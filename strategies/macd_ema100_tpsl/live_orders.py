from binance.enums import (
    ORDER_TYPE_LIMIT,
    ORDER_TYPE_STOP_LOSS_LIMIT,
    ORDER_TYPE_TAKE_PROFIT_LIMIT,
    SIDE_BUY,
    SIDE_SELL,
)
import state
import strategies.macd_ema100_tpsl.strategy_state as strategy_state
from strategies.macd_ema100_tpsl.utils.save_data import save_order
from config import SYMBOL, INTERVAL
from strategies.macd_ema100_tpsl.strategy_config import (
    STOP_LOSS_PERCENT,
    TAKE_PROFIT_PERCENT,
)
from utils.trading_helpers import (
    adjust_quantity_dor_coinUSDT,
    adjust_quantity_for_coin1,
    adjust_tick_size,
)

# Lista de órdenes abiertas
strategy_state.open_orders = []


def place_order_live(order_type, candle):
    """Coloca una orden LIMIT con Stop Loss y Take Profit en Binance."""
    if state.client is None:
        return
    price = float(candle["close"])
    quantity_usdt = adjust_quantity_dor_coinUSDT(
        state.balance_coin_USDT * 0.5 / price,
        state.step_size,
    )
    quantity_ltc = adjust_quantity_for_coin1(
        state.balance_coin_1 * 0.5, state.step_size
    )
    quantity = quantity_usdt if order_type == "BUY" else quantity_ltc
    stop_loss = (
        price * (1 - STOP_LOSS_PERCENT / 100)
        if order_type == "BUY"
        else price * (1 + STOP_LOSS_PERCENT / 100)
    )
    take_profit = (
        price * (1 + TAKE_PROFIT_PERCENT / 100)
        if order_type == "BUY"
        else price * (1 - TAKE_PROFIT_PERCENT / 100)
    )
    stop_loss = adjust_tick_size(stop_loss, state.tick_size)
    take_profit = adjust_tick_size(take_profit, state.tick_size)

    # 🟢 Crear orden LIMIT para entrar
    print(order_type)
    print(f"qty: {quantity} price: {price} sl: {stop_loss} tp: {take_profit}")
    order = state.client.create_order(
        symbol=SYMBOL.value,
        side=SIDE_BUY if order_type == "BUY" else SIDE_SELL,
        type=ORDER_TYPE_LIMIT,
        timeInForce="GTC",
        quantity=quantity,
        price=str(price),
    )
    state.update_balance2()

    print("Stop loss")
    # 🛑 Crear orden STOP LOSS
    stop_loss_order = state.client.create_order(
        symbol=SYMBOL.value,
        side=SIDE_SELL if order_type == "BUY" else SIDE_BUY,
        type=ORDER_TYPE_STOP_LOSS_LIMIT,
        timeInForce="GTC",
        quantity=quantity,
        stopPrice=str(stop_loss),
        price=str(stop_loss),
    )
    state.update_balance2()
    print("Take profit")
    # 🚀 Crear orden TAKE PROFIT
    take_profit_order = state.client.create_order(
        symbol=SYMBOL.value,
        side=SIDE_SELL if order_type == "BUY" else SIDE_BUY,
        type=ORDER_TYPE_TAKE_PROFIT_LIMIT,
        timeInForce="GTC",
        quantity=quantity,
        stopPrice=str(take_profit),
        price=str(take_profit),
    )

    state.update_balance2()

    # Guardamos las órdenes activas
    strategy_state.open_orders.append(
        {
            "entry_order": order,
            "stop_loss_order": stop_loss_order,
            "take_profit_order": take_profit_order,
            "order_type": order_type,
            "price_entry": price,
            "stop_loss": stop_loss,
            "take_profit": take_profit,
        }
    )

    print(
        f"🟢 {order_type} order placed at {price:.2f} | SL: {stop_loss:.2f} | TP: {take_profit:.2f}"
    )


def check_orders_live():
    """Revisa si alguna orden ha sido ejecutada o cerrada en Binance."""
    if state.client is None:
        return

    closed_orders = []

    for order_data in strategy_state.open_orders:
        entry_order_id = order_data["entry_order"]["orderId"]
        stop_loss_order_id = order_data["stop_loss_order"]["orderId"]
        take_profit_order_id = order_data["take_profit_order"]["orderId"]

        # Revisamos el estado de las órdenes
        entry_order_status = state.client.get_order(
            symbol=SYMBOL.value, orderId=entry_order_id
        )["status"]
        stop_loss_order_status = state.client.get_order(
            symbol=SYMBOL.value, orderId=stop_loss_order_id
        )["status"]
        take_profit_order_status = state.client.get_order(
            symbol=SYMBOL.value, orderId=take_profit_order_id
        )["status"]

        if entry_order_status == "FILLED":
            print(
                f"✅ Entrada ejecutada para {order_data['order_type']} en {order_data['price_entry']:.2f}"
            )

        if stop_loss_order_status == "FILLED":
            closed_orders.append((order_data, "SL"))
            state.update_balance2()

        if take_profit_order_status == "FILLED":
            closed_orders.append((order_data, "TP"))
            state.update_balance2()

    # Guardar y eliminar órdenes cerradas
    for order, reason in closed_orders:
        save_order(
            transact_time=order["entry_order"]["transactTime"],  # Tiempo de entrada
            exit_time=state.client.get_server_time()[
                "serverTime"
            ],  # Tiempo actual en Binance
            order_type=order["order_type"],
            price_order=order["price_entry"],
            interval=INTERVAL.value,
            symbol=SYMBOL.value,
            csv_filename=state.csv_file_name,
            exit_reason=reason,
        )
        strategy_state.open_orders.remove(order)
        print(f"🔴 {order['order_type']} order closed | Reason: {reason}")
