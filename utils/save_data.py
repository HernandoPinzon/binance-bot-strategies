import csv
import os
from datetime import datetime

CSV_FILE = "trading_history.csv"


def save_order(
    order_type,
    price,
    quantity,
    fee,
    profit_loss,
    balance,
    ema_short,
    ema_long,
    interval,
):
    """Guarda los datos de una orden en un archivo CSV"""
    file_exists = os.path.isfile(CSV_FILE)

    with open(CSV_FILE, mode="a", newline="") as file:
        writer = csv.writer(file)

        # Escribir encabezado si el archivo es nuevo
        if not file_exists:
            writer.writerow(
                [
                    "Timestamp",
                    "Order Type",
                    "Price",
                    "Quantity",
                    "Fee",
                    "Profit/Loss",
                    "Balance",
                    "EMA Short",
                    "EMA Long",
                    "Interval",
                ]
            )

        # Escribir la orden
        writer.writerow(
            [
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                order_type,
                price,
                quantity,
                fee,
                profit_loss,
                balance,
                ema_short,
                ema_long,
                interval,
            ]
        )

    print(f"💾 Orden guardada en {CSV_FILE}")
