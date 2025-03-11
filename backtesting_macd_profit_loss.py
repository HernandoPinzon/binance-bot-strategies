from datetime import datetime
from dotenv import load_dotenv
import state
from strategies.macd_ema100_tpsl.check_order import check_orders, place_order
from strategies.macd_ema100_tpsl.macd_plus_ema100 import (
    calculate_macd_plus_ema100,
    check_signals_macd_plus_ema100,
)
from strategies.macd_ema100_tpsl.utils.generate_csv_name import (
    generate_csv_name_with_config_macd_tpsl,
)
from utils.get_unique_filename import get_unique_filename
from utils.backtesting.data_fetcher import get_data_from_db

load_dotenv()

start_date = datetime(2025, 2, 1)
end_date = datetime(2025, 3, 10)
initial_candles = 100

state.csv_file_name = get_unique_filename(
    generate_csv_name_with_config_macd_tpsl("macd_plus_ema100")
)


def main():
    db_data = get_data_from_db(start_date, end_date)
    # Verificar que hay suficientes datos
    if len(db_data) < initial_candles:
        raise ValueError(
            f"Se necesitan al menos {initial_candles} velas para comenzar."
        )
    for i in range(initial_candles, len(db_data)):
        if i % (len(db_data) // 10) == 0:
            print(f"{i / len(db_data) * 100:.0f}%")
        candles_to_check = db_data.iloc[i - initial_candles : i + 1]

        df = calculate_macd_plus_ema100(candles_to_check.copy())

        # enviar 100 velas
        signal, last_candle_checked = check_signals_macd_plus_ema100(df)

        if signal in ["BUY", "SELL"]:
            next_candle = db_data.iloc[i + 1] if i + 1 < len(db_data) else None
            if next_candle is not None:
                place_order(
                    signal,
                    last_candle_checked,
                )

        check_orders(last_candle_checked)


if __name__ == "__main__":
    main()
