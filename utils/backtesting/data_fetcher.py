import time
import psycopg2
import pandas as pd
from config import SYMBOL, INTERVAL


def get_data_from_db(start_time, end_time):
    """Obtiene datos de la base de datos en un rango de tiempo."""
    conn = psycopg2.connect(
        host="localhost", database="timescaledb", user="postgres", password="password"
    )
    query = """
        SELECT timestamp, open, high, low, close, volume 
        FROM candlesticks 
        WHERE symbol = %s 
        AND timestamp BETWEEN %s AND %s 
        ORDER BY timestamp
    """
    df = pd.read_sql_query(query, conn, params=(SYMBOL.value, start_time, end_time))
    conn.close()
    return df
