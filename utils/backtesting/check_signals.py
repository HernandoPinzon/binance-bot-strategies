import pandas as pd
from config import EMA_LONG_PERIOD, EMA_SHORT_PERIOD, OrderTypes
from utils.trading_helpers import calculate_ema

previous_ema_diff_percentage = None


def check_signals(df):
    # Crear una copia explícita del DataFrame para evitar el warning
    df = df.copy()

    # Calcular EMAs
    df["EMA_10"] = calculate_ema(df, EMA_SHORT_PERIOD)
    df["EMA_50"] = calculate_ema(df, EMA_LONG_PERIOD)

    # Obtener la última y la penúltima fila
    last_row = df.iloc[-1]
    prev_row = df.iloc[-2]

    # Detectar señales
    if (
        prev_row["EMA_10"] < prev_row["EMA_50"]
        and last_row["EMA_10"] > last_row["EMA_50"]
    ):
        return "BUY", last_row
    if (
        prev_row["EMA_10"] > prev_row["EMA_50"]
        and last_row["EMA_10"] < last_row["EMA_50"]
    ):
        return "SELL", last_row
    # Si no hay señal, mantener
    return "HOLD", last_row
