import state
import math


def get_min_notional(symbol, client):
    """Obtiene el mínimo de notional permitido para un par"""
    exchange_info = client.get_exchange_info()
    for s in exchange_info["symbols"]:
        if s["symbol"] == symbol:
            for f in s["filters"]:
                if f["filterType"] == "NOTIONAL":
                    return float(f["minNotional"])
    return None  # Si no se encuentra el filtro


def calculate_ema(df, period):
    return df["close"].ewm(span=period, adjust=False).mean()


def get_trade_sizes(symbol, client):
    """
    Obtiene el tamaño mínimo y máximo de trade permitido en Binance para un símbolo específico.

    Parámetros:
        symbol (str): El par de trading (ejemplo: 'BTCUSDT').
        client (BinanceClient): Instancia del cliente de Binance.

    Retorna:
        tuple: (minQty, maxQty, stepSize) como flotantes.
    """
    try:
        exchange_info = client.get_exchange_info()
        for s in exchange_info["symbols"]:
            if s["symbol"] == symbol:
                for f in s["filters"]:
                    if f["filterType"] == "LOT_SIZE":
                        min_qty = float(f["minQty"])
                        max_qty = float(f["maxQty"])
                        step_size = float(f["stepSize"])
                        return min_qty, max_qty, step_size
    except Exception as e:
        print(f"Error al obtener los tamaños de trade: {e}")

    return None, None, None  # En caso de error


def adjust_quantity(quantity, step_size):
    quantity = float(quantity)
    step_size = float(step_size)

    # Ajustar al múltiplo más cercano de step_size
    adjusted_quantity = math.floor(quantity / step_size) * step_size

    # Verificar si cumple con el mínimo notional
    if adjusted_quantity < state.min_notional:
        print(
            f"Orden rechazada: {adjusted_quantity} es menor que el mínimo requerido {state.min_notional}"
        )

    # Redondear a la precisión correcta
    decimals = len(str(step_size).split(".")[1]) if "." in str(step_size) else 0
    return round(adjusted_quantity, decimals)


def adjust_quantity_dor_coinUSDT(quantity, step_size):
    quantity = float(quantity)
    step_size = float(step_size)

    # Ajustar al múltiplo más cercano de step_size
    adjusted_quantity = math.floor(quantity / step_size) * step_size

    # Verificar si cumple con el mínimo notional
    if adjusted_quantity * state.init_price < state.min_notional:
        print(
            f"Orden rechazada: {adjusted_quantity} es menor que el mínimo requerido {state.min_notional}"
        )

    # Redondear a la precisión correcta
    decimals = len(str(step_size).split(".")[1]) if "." in str(step_size) else 0
    return round(adjusted_quantity, decimals)


def adjust_quantity_for_coin1(quantity, step_size):
    quantity = float(quantity)
    step_size = float(step_size)

    # Ajustar al múltiplo más cercano de step_size
    adjusted_quantity = math.floor(quantity / step_size) * step_size

    # Verificar si cumple con el mínimo notional
    if adjusted_quantity < state.min_notional:
        print(
            f"Orden rechazada: {adjusted_quantity} es menor que el mínimo requerido {state.min_notional}"
        )

    # Redondear a la precisión correcta
    decimals = len(str(step_size).split(".")[1]) if "." in str(step_size) else 0
    return round(adjusted_quantity, decimals)


def adjust_tick_size(price, tick_size):
    price = float(price)
    tick_size = float(tick_size)

    # Ajustar al múltiplo más cercano de tick_size
    adjusted_price = math.floor(price / tick_size) * tick_size

    # Redondear a la precisión correcta
    decimals = len(str(tick_size).split(".")[1]) if "." in str(tick_size) else 0
    return round(adjusted_price, decimals)