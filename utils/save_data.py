from services import save_to_csv
from datetime import datetime

# Archivo CSV y Base de datos
CSV_FILE = "trading_historyV2.csv"
DB_PATH = "trading_history.db"

# Columnas esperadas
HEADERS = [
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


def format_number(value):
    """Convierte un número a cadena con coma en lugar de punto."""
    return str(value).replace(".", ",")


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
    """Guarda una orden en CSV y SQL llamando a los servicios correspondientes."""

    # Datos formateados
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    row_data = [
        timestamp,
        order_type,
        format_number(price),
        format_number(quantity),
        format_number(fee),
        format_number(profit_loss),
        format_number(balance),
        format_number(ema_short),
        format_number(ema_long),
        interval,
    ]

    # Guardar en CSV
    save_to_csv(CSV_FILE, HEADERS, row_data)

    # Guardar en SQL (sin cambiar la coma para evitar problemas con cálculos)
    # save_to_sql(DB_PATH, "orders", HEADERS, row_data)
