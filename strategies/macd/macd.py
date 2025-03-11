import pandas as pd
import talib

def calculate_macd(df, fast_length=12, slow_length=26, signal_length=9):
    """
    Calcula el MACD, la señal y el histograma.
    
    :param df: DataFrame con los precios de cierre.
    :param fast_length: Período para la EMA rápida.
    :param slow_length: Período para la EMA lenta.
    :param signal_length: Período para la EMA de la señal.
    :return: DataFrame con las columnas MACD, Signal e Histogram.
    """
    df['MACD'], df['Signal'], df['Histogram'] = talib.MACD(df['close'], 
                                                           fastperiod=fast_length, 
                                                           slowperiod=slow_length, 
                                                           signalperiod=signal_length)
    return df

def check_signals_macd(df):
    """
    Detecta señales de compra y venta basadas en el MACD.
    
    :param df: DataFrame con los datos del MACD.
    :return: Señal de compra/venta y la última fila.
    """
    # Crear una copia explícita del DataFrame para evitar el warning
    df = df.copy()
    
    # Obtener la última y la penúltima fila
    last_row = df.iloc[-1]
    prev_row = df.iloc[-2]
    
    # Detectar señales de compra (crossover)
    if prev_row['Histogram'] < 0 and last_row['Histogram'] >= 0:
        return "BUY", last_row
    
    # Detectar señales de venta (crossunder)
    if prev_row['Histogram'] > 0 and last_row['Histogram'] <= 0:
        return "SELL", last_row
    
    # Si no hay señal, mantener
    return "HOLD", last_row