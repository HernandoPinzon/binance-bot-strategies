import pandas as pd
import time
import state
from utils.ccxt_client import exchange
from config import SYMBOL, INTERVAL


def get_data(queue_trading, _):
    if state.client is None:
        return
    first_run = True
    historical_df = pd.DataFrame()
    last_price = None
    last_candle_time = None

    while True:
        limit = 100 if first_run else 1

        try:
            # 🔹 Obtener datos de velas de futuros
            response = state.client.futures_klines(
                symbol=SYMBOL.value, interval=INTERVAL.value, limit=limit
            )

            # 🔹 Convertir los datos en DataFrame
            new_df = pd.DataFrame(
                response,
                columns=[
                    "timestamp",
                    "open",
                    "high",
                    "low",
                    "close",
                    "volume",
                    "close_time",
                    "quote_asset_volume",
                    "num_trades",
                    "taker_buy_base",
                    "taker_buy_quote",
                    "ignore",
                ],
            )

            new_df = new_df[["timestamp", "open", "high", "low", "close", "volume"]]
            new_df["timestamp"] = pd.to_datetime(new_df["timestamp"], unit="ms")
            new_df["close"] = new_df["close"].astype(float)

            if first_run:
                historical_df = new_df
                first_run = False
            else:
                if new_df.iloc[-1]["timestamp"] != historical_df.iloc[-1]["timestamp"]:
                    historical_df = pd.concat(
                        [historical_df, new_df], ignore_index=True
                    ).tail(100)

            while not queue_trading.empty():
                queue_trading.get()
            queue_trading.put(historical_df)

            last_row = historical_df.iloc[-1]
            last_time = last_row["timestamp"].strftime("%H:%M")

            if last_row["close"] != last_price or last_time != last_candle_time:
                print(f"time_candle: {last_time}, {last_row['close']}")
                last_price = last_row["close"]
                last_candle_time = last_time

        except Exception as e:
            print(f"❌ Error al obtener datos: {e}")

        time.sleep(1)
