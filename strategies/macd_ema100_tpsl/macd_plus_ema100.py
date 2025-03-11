import pandas as pd
import talib


def calculate_macd_plus_ema100(df, fast_length=12, slow_length=26, signal_length=9):
    """
    Calcula el MACD, la señal y el histograma.

    :param df: DataFrame con los precios de cierre.
    :param fast_length: Período para la EMA rápida.
    :param slow_length: Período para la EMA lenta.
    :param signal_length: Período para la EMA de la señal.
    :return: DataFrame con las columnas MACD, Signal, Histogram y EMA100.
    """
    df["MACD"], df["Signal"], df["Histogram"] = talib.MACD(
        df["close"],
        fastperiod=fast_length,
        slowperiod=slow_length,
        signalperiod=signal_length,
    )

    # Calcular la EMA de 100 períodos
    df["EMA100"] = talib.EMA(df["close"], timeperiod=100)

    return df


def check_signals_macd_plus_ema100(df):
    """
    Detecta señales de compra y venta basadas en el MACD y la EMA100.

    :param df: DataFrame con los datos del MACD y la EMA100.
    :return: Señal de compra/venta y la última fila.
    """
    # Crear una copia explícita del DataFrame para evitar el warning
    df = df.copy()

    # Obtener la última y la penúltima fila
    last_row = df.iloc[-1]
    prev_row = df.iloc[-2]

    # Verificar si el precio está por encima o por debajo de la EMA100
    price_above_ema = last_row["close"] > last_row["EMA100"] * 1.003
    price_below_ema = last_row["close"] < last_row["EMA100"] * 0.997

    # Detectar señales de compra (crossover) solo si el precio está sobre la EMA100
    if prev_row["Histogram"] < 0 and last_row["Histogram"] >= 0 and price_above_ema:
        return "BUY", last_row

    # Detectar señales de venta (crossunder) solo si el precio está debajo de la EMA100
    if prev_row["Histogram"] > 0 and last_row["Histogram"] <= 0 and price_below_ema:
        return "SELL", last_row

    # Si no hay señal, mantener
    return "HOLD", last_row
