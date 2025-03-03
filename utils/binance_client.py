from binance.client import Client
import os
from dotenv import load_dotenv


def get_binance_client():
    load_dotenv()
    API_KEY = os.getenv("BINANCE_API_KEY")
    API_SECRET = os.getenv("BINANCE_API_SECRET")
    return Client(API_KEY, API_SECRET, testnet=True)
