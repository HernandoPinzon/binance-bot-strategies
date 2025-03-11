from config import INTERVAL, SYMBOL
from strategies.macd_ema100_tpsl.strategy_config import STOP_LOSS_PERCENT, TAKE_PROFIT_PERCENT


def generate_csv_name_with_config_macd_tpsl(name):
    return f"{name}_{SYMBOL.value}_sl{STOP_LOSS_PERCENT}_tp{TAKE_PROFIT_PERCENT}_"