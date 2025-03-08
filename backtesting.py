from datetime import datetime
from dotenv import load_dotenv
import state
from utils.generate_csv_name import generate_csv_name_with_config
from utils.get_unique_filename import get_unique_filename
from utils.backtesting.data_fetcher import get_data_from_db
from utils.backtesting.place_order import place_order
from utils.backtesting.check_signals import check_signals

load_dotenv()

start_date = datetime(2024, 11, 1)
end_date = datetime(2025, 2, 1)
initial_candles = 100

state.csv_file_name = get_unique_filename(
    generate_csv_name_with_config("inverse_precandle")
)


def main():
    db_data = get_data_from_db(start_date, end_date)
    # Verificar que hay suficientes datos
    if len(db_data) < initial_candles:
        raise ValueError(
            f"Se necesitan al menos {initial_candles} velas para comenzar."
        )
    # Bucle de trading
    last_signal = None  # Para evitar señales repetidas
    for i in range(initial_candles, len(db_data)):
        # Imprimir un punto cada 10% de las velas procesadas
        if i % (len(db_data) // 10) == 0:
            print(f"{i / len(db_data) * 100:.0f}%")
        candles_to_check = db_data.iloc[i - initial_candles : i + 1]

        # enviar 100 velas
        signal, last_candle_checked = check_signals(candles_to_check)

        if signal in ["BUY", "SELL"] and signal != last_signal:
            next_candle = db_data.iloc[i + 1] if i + 1 < len(db_data) else None
            if next_candle is not None:
                did_place_order = place_order(
                    signal,
                    last_candle_checked,
                    next_candle,
                )
                if did_place_order:
                    last_signal = signal


# ✅ Asegurar que el script se ejecuta correctamente en Windows
if __name__ == "__main__":
    main()
