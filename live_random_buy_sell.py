import random
import time

import pandas as pd
from config import COIN_NAMES, INTERVAL, SYMBOL
from strategies.macd_ema100_tpsl.live_orders import check_orders_live, place_order_live
from utils.binance_future_client import get_binance_future_client
from dotenv import load_dotenv
import state
from utils.ccxt_client import exchange

from utils.generate_csv_name import generate_csv_name_with_config
from utils.trading_helpers import get_trade_sizes

load_dotenv()
state.csv_file_name = generate_csv_name_with_config("live_random_buy_sell")
client = get_binance_future_client()
print(client.futures_account())

price = client.get_avg_price(symbol=SYMBOL.value)
exchange_info = client.get_symbol_info(SYMBOL.value)
state.init_price = float(price["price"])
state.min_trade_size, state.max_trade_size, state.step_size = get_trade_sizes(
    SYMBOL.value, client
)
coin_1 = client.get_asset_balance(asset=COIN_NAMES[0])
coin_2 = client.get_asset_balance(asset=COIN_NAMES[1])
if coin_1 is not None and coin_2 is not None:
    state.balance_coin_1 = float(coin_1["free"])
    state.balance_coin_USDT = float(coin_2["free"])
state.client = client


def main():
    # Bucle de trading
    while True:
        response = exchange.fetch_ohlcv(SYMBOL.value, timeframe=INTERVAL.value, limit=1)
        new_df = pd.DataFrame(
            response,
            columns=["timestamp", "open", "high", "low", "close", "volume"],
        )
        new_df["close"] = new_df["close"].astype(float)
        candle = new_df.iloc[-1]
        signal = random.choice(["BUY", "SELL"])
        if signal in ["BUY", "SELL"] and signal != state.last_signal:
            place_order_live(signal, candle)
        check_orders_live()
        time.sleep(5)


if __name__ == "__main__":
    if (
        state.balance_coin_1 is not None
        and state.balance_coin_USDT is not None
        and exchange_info is not None
    ):
        for f in exchange_info["filters"]:
            if f["filterType"] == "NOTIONAL":
                state.min_notional = float(f["minNotional"])
            if f["filterType"] == "PRICE_FILTER":
                state.tick_size = float(f["tickSize"])

        print(f"El mínimo notional permitido es: {state.min_notional}")
        print("Step size:", state.step_size)
        print("Tick size:", state.tick_size)
        print("Precio inicial:", state.init_price)
        print(f"Balance de {COIN_NAMES[0]}: {state.balance_coin_1}")
        print(f"Balance de {COIN_NAMES[1]}: {state.balance_coin_USDT}")
        if (
            state.balance_coin_1 * state.init_price <= state.min_notional
            or state.balance_coin_USDT <= state.min_notional
        ):
            state.adjust_balance()
        main()
