import psycopg2
import time
import pandas as pd
from datetime import datetime, timedelta
from config import DB_CONFIG, INTERVAL, SYMBOL
from utils.ccxt_client import exchange
from dotenv import load_dotenv

load_dotenv()


def connect_db():
    return psycopg2.connect(
        dbname=DB_CONFIG["name"],
        user=DB_CONFIG["user"],
        password=DB_CONFIG["password"],
        host=DB_CONFIG["host"],
        port=DB_CONFIG["port"],
    )


def create_table():
    with connect_db() as conn, conn.cursor() as cur:
        # 1. Crear tabla base
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS candlesticks (
                timestamp TIMESTAMPTZ NOT NULL,
                symbol TEXT NOT NULL,
                open DOUBLE PRECISION,
                high DOUBLE PRECISION,
                low DOUBLE PRECISION,
                close DOUBLE PRECISION,
                volume DOUBLE PRECISION,
                PRIMARY KEY (symbol, timestamp)
            );
        """
        )

        # 2. Convertir a hypertable
        cur.execute(
            """
            SELECT create_hypertable(
                'candlesticks',
                'timestamp',
                if_not_exists => TRUE,
                chunk_time_interval => INTERVAL '7 days'
            );
        """
        )

        # 3. Crear índices
        cur.execute(
            """
            CREATE INDEX IF NOT EXISTS ix_symbol_time 
            ON candlesticks (symbol, timestamp DESC);
        """
        )

        conn.commit()


def fetch_historical_data(start_date, end_date):
    conn = connect_db()
    cursor = conn.cursor()

    current_start = start_date
    batch_size = 1000  # Máximo permitido por Binance

    while current_start < end_date:
        try:
            # Check API usage
            headers = exchange.last_response_headers
            if headers:
                used_weight = int(headers.get("X-MBX-USED-WEIGHT-1M", 0))
                if used_weight >= 6000:
                    print(
                        f"⚠️ Uso actual de API: {used_weight} / 6000 (1 min). Pausando..."
                    )
                    time.sleep(60)  # Pausar por 1 minuto
                    continue

            # Fetch datos de Binance
            candles = exchange.fetch_ohlcv(
                SYMBOL.value,
                timeframe=INTERVAL.value,
                since=int(current_start.timestamp() * 1000),
                limit=batch_size,
            )

            # Check API usage again after fetch
            headers = exchange.last_response_headers
            if headers:
                used_weight = int(headers.get("X-MBX-USED-WEIGHT-1M", 0))
                print(f"⚠️ Uso actual de API: {used_weight} / 6000 (1 min)")

            if not candles:
                break

            # Convertir a DataFrame
            df = pd.DataFrame(
                candles, columns=["timestamp", "open", "high", "low", "close", "volume"]
            )
            df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
            df["symbol"] = SYMBOL.value

            # Insertar en TimescaleDB
            for _, row in df.iterrows():
                cursor.execute(
                    """
                    INSERT INTO candlesticks 
                    (timestamp, symbol, interval, open, high, low, close, volume)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT DO NOTHING
                    """,
                    (
                        row["timestamp"],
                        row["symbol"],
                        INTERVAL.value,  # Agregar la temporalidad
                        row["open"],
                        row["high"],
                        row["low"],
                        row["close"],
                        row["volume"],
                    ),
                )

            conn.commit()
            print(
                f"Insertados datos desde {df['timestamp'].iloc[0]} hasta {df['timestamp'].iloc[-1]}"
            )

            # Actualizar el puntero temporal
            current_start = df["timestamp"].iloc[-1] + pd.Timedelta(minutes=1)

            # Respeta el rate limit
            time.sleep(exchange.rateLimit / 1000)  # Convertir ms a segundos

        except Exception as e:
            print(f"Error: {e}")
            time.sleep(60)
            conn.rollback()

    cursor.close()
    conn.close()


def check_table_exists():
    with connect_db() as conn, conn.cursor() as cur:
        cur.execute("SELECT current_database();")
        db_name = cur.fetchone()
        if db_name:
            print(f"Conectado a la base de datos: {db_name}")
        else:
            print("No se pudo conectar a la base de datos")

        cur.execute(
            """
            SELECT EXISTS (
                SELECT 1 FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name = 'candlesticks'
            );
        """
        )
        exists = cur.fetchone()
        if exists and exists[0]:
            print("La tabla 'candlesticks' EXISTE")
        else:
            print("La tabla 'candlesticks' NO EXISTE")
        return exists


check_table_exists()


if __name__ == "__main__":
    # create_table()
    start_date = datetime(2024, 5, 1)
    end_date = datetime(2025, 3, 10)
    fetch_historical_data(start_date, end_date)
