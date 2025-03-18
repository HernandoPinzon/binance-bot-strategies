from multiprocessing import Process, Queue
import time
from config import COIN_NAMES, LEVERAGE, SYMBOL
from strategies.macd_ema100_tpsl.live_orders2 import place_future_order
from strategies.macd_ema100_tpsl.macd_plus_ema100 import (
    calculate_macd_plus_ema100,
    check_signals_macd_plus_ema100,
)
from utils.binance_client import get_binance_future_client
from utils.data_fetcher_futures import get_data
from dotenv import load_dotenv
import state
from utils.trading_helpers import get_trade_sizes

load_dotenv()
state.strategy = "macd"
client = get_binance_future_client()
price = client.get_avg_price(symbol=SYMBOL.value)
exchange_info = client.get_symbol_info(SYMBOL.value)
state.init_price = float(price["price"])
state.min_trade_size, state.max_trade_size, state.step_size = get_trade_sizes(
    SYMBOL.value, client
)
state.client = client
state.update_balance3()
client.futures_change_leverage(symbol=SYMBOL.value, leverage=LEVERAGE)


def main():
    queue_trading = Queue()
    queue_plot = Queue()  # No se usa, pero se mantiene para evitar errores

    # Crear proceso para obtener datos
    data_process = Process(target=get_data, args=(queue_trading, queue_plot))
    data_process.start()

    # Esperar hasta que haya datos en la cola de trading
    print("Esperando datos de Binance", end="")
    while queue_trading.empty():
        print(".", end="")
        time.sleep(1)
    print("\nDatos recibidos")

    # Bucle de trading
    while True:
        if queue_trading.empty():
            continue
        data = queue_trading.get()
        df = calculate_macd_plus_ema100(
            df=data, ema=100, fast_length=12, slow_length=26, signal_length=9
        )
        result = check_signals_macd_plus_ema100(
            df, ema_length_down=0.3, ema_length_up=0.4
        )
        if result is not None:
            signal, candle = result
            if signal in ["BUY", "SELL"]:
                print(f"Señal: {signal}")
                place_future_order(signal, candle)
        time.sleep(1)


if __name__ == "__main__":
    if (
        state.balance_coin_1 is not None
        and state.balance_coin_USDT is not None
        and exchange_info is not None
    ):
        for f in exchange_info["filters"]:
            if f["filterType"] == "NOTIONAL":
                state.min_notional = float(f["minNotional"])
                break
        print(f"El mínimo notional permitido es: {state.min_notional}")
        print("Precio inicial:", state.init_price)
        print(f"Balance de {COIN_NAMES[1]}: {state.balance_coin_USDT}")
        main()
