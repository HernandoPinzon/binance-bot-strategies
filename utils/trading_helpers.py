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
    """Calcula la media móvil exponencial (EMA)"""
    return df["close"].ewm(span=period, adjust=False).mean()
