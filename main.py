from multiprocessing import Process, Queue
import time
from config import ENABLE_PLOT
from strategies.ema_strategy import check_signals, place_order
from utils.binance_client import get_binance_client
from utils.data_fetcher import get_data
from utils.live_plot import live_plot
from dotenv import load_dotenv

load_dotenv()
client = get_binance_client()


def main():
    queue_trading = Queue()  # Cola para el bot de trading
    queue_plot = Queue()  # Cola separada para el gráfico

    # Crear proceso para obtener datos
    data_process = Process(target=get_data, args=(queue_trading, queue_plot))
    data_process.start()

    if ENABLE_PLOT:
        plot_process = Process(target=live_plot, args=(queue_plot,))
        plot_process.start()

    # Esperar hasta que haya datos en la cola de trading
    print("Esperando datos de Binance...")
    while queue_trading.empty():
        print("...")
        time.sleep(1)

    print("Datos recibidos")
    # Bucle de trading
    while True:
        signal = check_signals(queue_trading)
        if signal in ["BUY", "SELL"]:
            place_order(signal, client)

        time.sleep(60)


# ✅ Asegurar que el script se ejecuta correctamente en Windows
if __name__ == "__main__":
    main()
