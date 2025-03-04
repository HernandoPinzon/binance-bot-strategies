from services import save_to_csv
from datetime import datetime

# Archivo CSV y Base de datos
CSV_FILE = "trading_historyV4.csv"
DB_PATH = "trading_history.db"

# Columnas esperadas
HEADERS = [
    "Timestamp",
    "Order Type",
    "Price",
    "Quantity",
    "EMA Short",
    "EMA Long",
    "Interval",
    "Symbol",
]


def format_number(value):
    """Convierte un número a cadena con coma en lugar de punto."""
    return str(value).replace(".", ",")


def save_order(
    transact_time,
    order_type,
    price,
    quantity,
    ema_short,
    ema_long,
    interval,
    symbol,
):
    """Guarda una orden en CSV y SQL llamando a los servicios correspondientes."""

    row_data = [
        transact_time,
        order_type,
        format_number(price),
        format_number(quantity),
        format_number(ema_short),
        format_number(ema_long),
        interval,
        symbol,
    ]

    # Guardar en CSV
    save_to_csv(CSV_FILE, HEADERS, row_data)

    # Guardar en SQL (sin cambiar la coma para evitar problemas con cálculos)
    # save_to_sql(DB_PATH, "orders", HEADERS, row_data)
