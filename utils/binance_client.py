from binance.client import Client
import os



def get_binance_client():
    API_KEY = os.getenv("BINANCE_API_KEY")
    API_SECRET = os.getenv("BINANCE_API_SECRET")
    return Client(API_KEY, API_SECRET, testnet=True)
