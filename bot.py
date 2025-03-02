import os
from binance.client import Client
from dotenv import load_dotenv

# Cargar claves desde .env
load_dotenv()
API_KEY = os.getenv("BINANCE_TESTNET_API_KEY")
API_SECRET = os.getenv("BINANCE_TESTNET_SECRET_KEY")

# Conectar a la Testnet (IMPORTANTE: usar testnet=True)
client = Client(API_KEY, API_SECRET, testnet=True)

# Obtener saldo en la Testnet
balance =   client.get_account()
print(balance)

# Crear una orden de prueba
order = client.create_order(
    symbol='BTCUSDT',
    side='BUY',
    type='MARKET',
    quantity=0.001
)
print(order)
