from multiprocessing import Process, Queue
import time
from config import COIN_NAMES, SYMBOL
from strategies.ema_inverse_strategy2 import place_order_inverse
from strategies.ema_strategy import check_signals
from utils.binance_client import get_binance_client
from utils.data_fetcher import get_data
from dotenv import load_dotenv
import state

from utils.generate_csv_name import generate_csv_name_with_config
from utils.trading_helpers import get_trade_sizes

load_dotenv()
state.csv_file_name = generate_csv_name_with_config("inverse_precandle_live_v2")
client = get_binance_client()
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
        result = check_signals(queue_trading)
        if result is not None:
            signal, candle = result
            if signal in ["BUY", "SELL"] and signal != state.last_signal:
                place_order_inverse(signal, candle)
        time.sleep(1)


# ✅ Asegurar que el script se ejecuta correctamente en Windows
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
        print(f"Balance de {COIN_NAMES[0]}: {state.balance_coin_1}")
        print(f"Balance de {COIN_NAMES[1]}: {state.balance_coin_USDT}")
        if (
            state.balance_coin_1 * state.init_price <= state.min_notional
            or state.balance_coin_USDT <= state.min_notional
        ):
            state.adjust_balance()
        main()
