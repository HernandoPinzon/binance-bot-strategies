import pandas as pd
import time
from utils.ccxt_client import exchange
from config import SYMBOL, INTERVAL


def get_data(queue_trading, queue_plot):
    """Obtiene datos de Binance y los envía a la cola compartida.
    - La primera vez trae 100 datos (histórico).
    - Luego, solo agrega 1 nuevo dato en cada iteración.
    """

    first_run = True  # Flag para saber si es la primera ejecución
    historical_df = pd.DataFrame()  # DataFrame para almacenar histórico

    while True:
        if first_run:
            limit = 100  # 🔹 Primera vez: Pedimos 100 datos
        else:
            limit = 1  # 🔹 Después: Pedimos solo 1 nuevo

        ohlcv = exchange.fetch_ohlcv(
            SYMBOL.value, timeframe=INTERVAL.value, limit=limit
        )

        new_df = pd.DataFrame(
            ohlcv, columns=["timestamp", "open", "high", "low", "close", "volume"]
        )
        new_df["close"] = new_df["close"].astype(float)
        new_df["timestamp"] = pd.to_datetime(new_df["timestamp"], unit="ms")

        if first_run:
            historical_df = new_df  # Guardar los primeros 100 datos
            first_run = False  # Desactivar la flag
        else:
            if new_df.iloc[-1]["timestamp"] != historical_df.iloc[-1]["timestamp"]:
                historical_df = pd.concat(
                    [historical_df, new_df], ignore_index=True
                ).tail(
                    100
                )  # Mantener máximo 100 registros

        while not queue_trading.empty():
            queue_trading.get()
        while not queue_plot.empty():
            queue_plot.get()

        # 🔹 Enviar datos a ambas colas
        queue_trading.put(historical_df)
        queue_plot.put(historical_df)

        time.sleep(5)  # Espera antes de la siguiente llamada
