import time
import pandas as pd
import ccxt
import psycopg2
from datetime import datetime, timedelta
from config import SYMBOL, INTERVAL, DB_CONFIG

# Configurar conexión a TimescaleDB
def connect_db():
    return psycopg2.connect(
        dbname=DB_CONFIG['dbname'],
        user=DB_CONFIG['user'],
        password=DB_CONFIG['password'],
        host=DB_CONFIG['host'],
        port=DB_CONFIG['port']
    )

def create_table():
    with connect_db() as conn, conn.cursor() as cur:
        cur.execute('''
            CREATE TABLE IF NOT EXISTS candlesticks (
                timestamp TIMESTAMPTZ PRIMARY KEY,
                open DOUBLE PRECISION,
                high DOUBLE PRECISION,
                low DOUBLE PRECISION,
                close DOUBLE PRECISION,
                volume DOUBLE PRECISION
            );
        ''')
        conn.commit()

def save_to_db(data):
    with connect_db() as conn, conn.cursor() as cur:
        for row in data:
            cur.execute(
                "INSERT INTO candlesticks (timestamp, open, high, low, close, volume) VALUES (%s, %s, %s, %s, %s, %s) ON CONFLICT (timestamp) DO NOTHING;",
                row,
            )
        conn.commit()

exchange = ccxt.binance({})

def fetch_historical_data(start_date, end_date):
    since = int(start_date.timestamp() * 1000)
    end_ts = int(end_date.timestamp() * 1000)
    all_data = []
    
    while since < end_ts:
        try:
            candles = exchange.fetch_ohlcv(SYMBOL.value, timeframe=INTERVAL.value, since=since, limit=500)
            if not candles:
                break
            
            last_timestamp = candles[-1][0]
            since = last_timestamp + 1
            all_data.extend([(pd.to_datetime(c[0], unit='ms'), *c[1:]) for c in candles])
            
            time.sleep(1)  # Evitar exceso de llamadas a la API
        except Exception as e:
            print(f"Error: {e}")
            time.sleep(5)
    
    save_to_db(all_data)
    print(f"Guardados {len(all_data)} registros en la base de datos.")

if __name__ == "__main__":
    create_table()
    from datetime import timezone
    start = datetime.now(timezone.utc) - timedelta(days=365)  # Último año
    end = datetime.now(timezone.utc)
    fetch_historical_data(start, end)
