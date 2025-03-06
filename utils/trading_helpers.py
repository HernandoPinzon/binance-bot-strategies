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


def get_min_trade_size(symbol, client):
    """Obtiene el tamaño mínimo de orden para un símbolo en Binance"""
    exchange_info = client.get_exchange_info()
    for s in exchange_info["symbols"]:
        if s["symbol"] == symbol:
            for f in s["filters"]:
                if f["filterType"] == "LOT_SIZE":
                    return float(f["stepSize"])  # Tamaño mínimo permitido
    return 0.001
