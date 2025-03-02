import os
import pandas as pd
import time
import ccxt
from binance.client import Client
from dotenv import load_dotenv
import config  # Importamos el archivo de configuración

# Cargar claves API desde .env
load_dotenv()
API_KEY = os.getenv("BINANCE_TESTNET_API_KEY")
API_SECRET = os.getenv("BINANCE_TESTNET_SECRET_KEY")

# Conectar al cliente de Binance Testnet
client = Client(API_KEY, API_SECRET, testnet=True)
exchange = ccxt.binance(
    {
        "urls": {
            "api": {
                "public": "https://data-api.binance.vision/api/v3",
            },
        },
    }
)


def get_data():
    """Obtiene datos de mercado desde Binance"""
    ohlcv = exchange.fetch_ohlcv(
        config.SYMBOL.value, timeframe=config.INTERVAL.value, limit=100
    )
    df = pd.DataFrame(
        ohlcv, columns=["timestamp", "open", "high", "low", "close", "volume"]
    )
    df["close"] = df["close"].astype(float)
    return df


def calculate_ema(df, period):
    """Calcula la media móvil exponencial (EMA)"""
    return df["close"].ewm(span=period, adjust=False).mean()


def check_signals():
    """Verifica señales de compra o venta"""
    df = get_data()

    df["EMA_10"] = calculate_ema(df, config.EMA_SHORT_PERIOD)
    df["EMA_50"] = calculate_ema(df, config.EMA_LONG_PERIOD)

    last_row = df.iloc[-1]

    if last_row["EMA_10"] > last_row["EMA_50"]:
        return "BUY"
    elif last_row["EMA_10"] < last_row["EMA_50"]:
        return "SELL"
    return "HOLD"


def place_order(order_type):
    """Ejecuta una orden en Binance Testnet"""
    try:
        print(
            f"🔹 Enviando orden: {order_type} - Símbolo: {config.SYMBOL.value} - Cantidad: {config.QUANTITY}"
        )

        if order_type == "BUY":
            order = client.create_order(
                symbol=config.SYMBOL.value,
                side="BUY",
                type="MARKET",
                quantity=config.QUANTITY,
            )
            print("🟢 ORDEN DE COMPRA:", order)
        elif order_type == "SELL":
            order = client.create_order(
                symbol=config.SYMBOL.value,
                side="SELL",
                type="MARKET",
                quantity=config.QUANTITY,
            )
            print("🔴 ORDEN DE VENTA:", order)

    except Exception as e:
        print(f"❌ ERROR AL EJECUTAR ORDEN: {e}")


# Bucle de trading
while True:
    signal = check_signals()
    print(f"📊 Señal detectada: {signal}")

    if signal in ["BUY", "SELL"]:
        place_order(signal)

    time.sleep(60)  # Esperar 1 minuto antes de la próxima verificación
