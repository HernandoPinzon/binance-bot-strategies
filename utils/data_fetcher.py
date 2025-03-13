import pandas as pd
import time
from utils.ccxt_client import exchange
from config import SYMBOL, INTERVAL


def get_data(queue_trading, _):
    """Obtiene datos de Binance y los envía a la cola compartida.
    - La primera vez trae 100 datos (histórico).
    - Luego, solo agrega 1 nuevo dato en cada iteración.
    """

    first_run = True  # Flag para saber si es la primera ejecución
    historical_df = pd.DataFrame()  # DataFrame para almacenar histórico
    last_price = None
    last_candle_time = None

    while True:
        limit = 100 if first_run else 1  # 🔹 Primera vez: 100 datos, luego 1 dato nuevo

        try:
            # 🔹 Realizar la solicitud a Binance
            response = exchange.fetch_ohlcv(
                SYMBOL.value, timeframe=INTERVAL.value, limit=limit
            )

            # 🔹 Acceder a los headers de la respuesta
            headers = exchange.last_response_headers
            if headers:
                used_weight = headers.get("X-MBX-USED-WEIGHT-1M", "No disponible")

            # 🔹 Convertir los datos en DataFrame
            new_df = pd.DataFrame(
                response,
                columns=["timestamp", "open", "high", "low", "close", "volume"],
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
            queue_trading.put(historical_df)

            # 🔹 Imprimir el último precio y la fecha
            last_row = historical_df.iloc[-1]
            last_time = last_row["timestamp"].strftime("%H:%M")

            if last_row["close"] != last_price or last_time != last_candle_time:
                print(
                    f"time_candle: {last_time}, {last_row['close']}"
                )
                last_price = last_row["close"]
                last_candle_time = last_time

        except Exception as e:
            print(f"❌ Error al obtener datos: {e}")

        time.sleep(1) 
