from multiprocessing import Process, Queue
import time
from config import ENABLE_PLOT, INTERVAL, SYMBOL, IntervalsInSeconds
from strategies.ema_strategy import check_signals, place_order
from utils.binance_client import get_binance_client
from utils.data_fetcher import get_data
from utils.live_plot import live_plot
from dotenv import load_dotenv

from utils.trading_helpers import get_min_trade_size

load_dotenv()
client = get_binance_client()

# Obtener min_trade_size una sola vez
min_trade_size = get_min_trade_size(SYMBOL.value, client)


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

    last_signal = None  # Guarda la última señal ejecutada

    # Bucle de trading
    while True:
        result = check_signals(queue_trading)
        if result is not None:
            signal, current_price = result
            if signal in ["BUY", "SELL"] and signal != last_signal:
                place_order(signal, client, min_trade_size, current_price)
                last_signal = signal  # Actualizar la última señal ejecutada

        time.sleep(1)


# ✅ Asegurar que el script se ejecuta correctamente en Windows
if __name__ == "__main__":
    main()
