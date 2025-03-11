from services import save_to_csv

# Archivo CSV y Base de datos
DB_PATH = "trading_history.db"

# Columnas esperadas
HEADERS = [
    "Timestamp",
    "Order Type",
    "Price Order",
    "Interval",
    "Symbol",
    "Exit Reason",
]


def format_number(value):
    """Convierte un número a cadena con coma en lugar de punto."""
    return str(value).replace(".", ",")


def save_order(
    transact_time, order_type, price_order, interval, symbol, csv_filename, exit_reason
):
    """Guarda una orden en CSV y SQL llamando a los servicios correspondientes."""

    row_data = [
        transact_time,
        order_type,
        format_number(price_order),
        interval,
        symbol,
        exit_reason,
    ]

    # Guardar en CSV
    save_to_csv(csv_filename + ".csv", HEADERS, row_data)

    # Guardar en SQL (sin cambiar la coma para evitar problemas con cálculos)
    # save_to_sql(DB_PATH, "orders", HEADERS, row_data)
