import time
import csv
import os
import pandas as pd
from datetime import datetime, timedelta
from config import INTERVAL, SYMBOL
from utils.ccxt_client import exchange
from dotenv import load_dotenv

load_dotenv()

def save_to_csv(file_path, headers, row_data, delimiter=";"):
    """Guarda una fila en un archivo CSV, creando el archivo si no existe."""
    file_exists = os.path.isfile(file_path)

    with open(file_path, mode="a", newline="") as file:
        writer = csv.writer(file, delimiter=delimiter)

        # Escribir encabezado si el archivo es nuevo
        if not file_exists:
            writer.writerow(headers)

        # Escribir los datos en el archivo
        writer.writerows(row_data)

def fetch_and_save_to_csv(start_date, end_date, file_name="data.csv"):
    current_start = start_date
    batch_size = 1000  # Máximo permitido por Binance
    headers = ["timestamp", "open", "high", "low", "close", "volume"]
    
    while current_start < end_date:
        try:
            candles = exchange.fetch_ohlcv(
                SYMBOL.value,
                timeframe=INTERVAL.value,
                since=int(current_start.timestamp() * 1000),
                limit=batch_size,
            )
            
            if not candles:
                break
            
            row_data = [
                [pd.to_datetime(candle[0], unit="ms"), candle[1], candle[2], candle[3], candle[4], candle[5]]
                for candle in candles
            ]
            
            save_to_csv(file_name, headers, row_data)
            
            current_start = pd.to_datetime(candles[-1][0], unit="ms") + pd.Timedelta(minutes=1)
            time.sleep(exchange.rateLimit / 1000)
        except Exception as e:
            print(f"Error: {e}")
            time.sleep(60)

if __name__ == "__main__":
    start_date = datetime(2025, 3, 4)
    end_date = datetime(2025, 3, 5)
    fetch_and_save_to_csv(start_date, end_date, "binance_data.csv")