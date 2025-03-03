import matplotlib.pyplot as plt
import matplotlib.animation as animation
import pandas as pd
from utils.trading_helpers import calculate_ema
from config import EMA_SHORT_PERIOD, EMA_LONG_PERIOD
import time

def live_plot(queue):
    """Gráfica en vivo mostrando el precio y las líneas de EMA sin residuos"""
    fig, ax = plt.subplots()
    xdata, ydata = [], []
    ema_10_value, ema_50_value = None, None  # Últimos valores de EMA

    # 🔹 Esperar hasta que haya datos en la cola antes de iniciar
    print("Esperando primeros datos para inicializar el gráfico...")
    while queue.empty():
        time.sleep(1)

    # 🔹 Obtener los primeros 100 datos antes de iniciar la animación
    df = queue.get()
    xdata = df["timestamp"].tolist()[-100:]
    ydata = df["close"].tolist()[-100:]
    ema_10_value = calculate_ema(df, EMA_SHORT_PERIOD).iloc[-1]
    ema_50_value = calculate_ema(df, EMA_LONG_PERIOD).iloc[-1]

    def update(frame):
        nonlocal ema_10_value, ema_50_value

        if not queue.empty():
            df = queue.get()  # Obtener datos recientes

            # Agregar solo el último dato y eliminar el más antiguo si supera 100
            xdata.append(df["timestamp"].iloc[-1])
            ydata.append(df["close"].iloc[-1])
            if len(xdata) > 100:
                xdata.pop(0)
                ydata.pop(0)

            # Calcular los EMA solo con los datos más recientes
            ema_10_value = calculate_ema(df, EMA_SHORT_PERIOD).iloc[-1]
            ema_50_value = calculate_ema(df, EMA_LONG_PERIOD).iloc[-1]

            ax.clear()

            # Dibujar precio
            ax.plot(xdata, ydata, label="Precio BTC", color="blue")

            # Agregar líneas EMA horizontales
            ax.axhline(y=ema_10_value, color="orange", linestyle="--", label="EMA 10", xmin=0, xmax=1)
            ax.axhline(y=ema_50_value, color="red", linestyle="--", label="EMA 50", xmin=0, xmax=1)

            ax.legend()

    _ = animation.FuncAnimation(fig, update, interval=5000)
    plt.show()
