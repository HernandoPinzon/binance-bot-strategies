def check_signals_bar_up_down(df):
    # Crear una copia explícita del DataFrame para evitar el warning
    df = df.copy()

    # Obtener la última y la penúltima fila
    last_row = df.iloc[-1]
    prev_row = df.iloc[-2]

    # Detectar señales de Bar Up (señal de compra)
    if last_row["close"] > last_row["open"] and last_row["open"] > prev_row["close"]:
        return "BUY", last_row

    # Detectar señales de Bar Down (señal de venta)
    if last_row["close"] < last_row["open"] and last_row["open"] < prev_row["close"]:
        return "SELL", last_row

    # Si no hay señal, mantener
    return "HOLD", last_row
