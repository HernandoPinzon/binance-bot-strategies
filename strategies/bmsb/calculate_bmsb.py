import talib

from config import INTERVAL, SYMBOL
import state
from strategies.bmsb.save_data import save_order

previous_price = None


def calculate_bmsb(df, sma_period=20, ema_period=21):
    """
    Calcula la Bull Market Support Band (BMSB).

    :param df: DataFrame con los precios de cierre.
    :param sma_period: Período para la SMA.
    :param ema_period: Período para la EMA.
    :return: DataFrame con las columnas BMSB_Mayor y BMSB_Menor.
    """
    df["SMA"] = talib.SMA(df["close"], timeperiod=sma_period)
    df["EMA"] = talib.EMA(df["close"], timeperiod=ema_period)

    df["BMSB_Mayor"] = df[["SMA", "EMA"]].max(axis=1)
    df["BMSB_Menor"] = df[["SMA", "EMA"]].min(axis=1)

    return df


def check_signals_bmsb(df):
    """
    Detecta señales de compra y venta basadas en la BMSB.

    :param df: DataFrame con los datos de la BMSB.
    :return: Señal de compra/venta y la última fila.
    """
    df = df.copy()
    last_row = df.iloc[-1]
    prev_row = df.iloc[-2]

    buy_signal = (
        prev_row["close"] <= prev_row["BMSB_Mayor"]
        and last_row["close"] > last_row["BMSB_Mayor"]
    )
    sell_signal = (
        prev_row["close"] >= prev_row["BMSB_Menor"]
        and last_row["close"] < last_row["BMSB_Menor"]
    )

    if buy_signal:
        return "BUY", last_row
    if sell_signal:
        return "SELL", last_row

    return "HOLD", last_row


def place_order(order_type, candle, next_candle):
    """
    Maneja la ejecución de órdenes y actualiza el balance de capital.

    :param order_type: Tipo de orden ('BUY' o 'SELL').
    :param candle: Vela en la que se genera la señal.
    :param next_candle: Vela en la que se ejecuta la orden.
    :param capital: Capital actual disponible.
    :param order_size: Porcentaje del capital a usar en cada orden.
    :return: Nuevo capital después de la orden.
    """
    global previous_price
    transact_time = next_candle["timestamp"].strftime("%Y-%m-%d %H:%M:%S")
    order_amount = state.capital_usdt * state.order_size

    if order_type == "BUY":
        for trade in state.trades:
            if trade["order_type"] == "SELL":
                vendi = trade["quantity"] / trade["price_order"]
                compro = vendi * candle["close"]
                state.capital_usdt = state.capital_usdt + compro
                trade["filled"] = True
        state.trades.append(
            {
                "order_type": order_type,
                "price_order": candle["close"],
                "quantity": order_amount,
                "filled": False,
            }
        )
    else:
        for trade in state.trades:
            if trade["order_type"] == "BUY":
                compre = trade["quantity"] / trade["price_order"]
                vendo = compre * candle["close"]
                print(f"Compre: {compre} a {trade['price_order']}")
                print(f"Vendo: {vendo} a {candle['close']}")
                state.capital_usdt = state.capital_usdt + vendo
                trade["filled"] = True
        state.trades.append(
            {
                "order_type": order_type,
                "price_order": candle["close"],
                "quantity": order_amount,
                "filled": False,
            }
        )
    # eliminar trades llenados
    state.trades = [trade for trade in state.trades if not trade["filled"]]
    capital = state.capital_usdt
    state.capital_usdt -= order_amount
    save_order(
        transact_time=transact_time,
        order_type=order_type,
        price_order=candle["close"],
        interval=INTERVAL.value,
        symbol=SYMBOL.value,
        capital=capital,
        csv_filename=state.csv_file_name,
    )
