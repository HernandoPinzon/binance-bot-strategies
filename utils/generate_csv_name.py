from config import EMA_LONG_PERIOD, EMA_SHORT_PERIOD, INTERVAL, SYMBOL


def generate_csv_name_with_config(name):
    return f"{name}_{SYMBOL.value}_{EMA_SHORT_PERIOD}_{EMA_LONG_PERIOD}"