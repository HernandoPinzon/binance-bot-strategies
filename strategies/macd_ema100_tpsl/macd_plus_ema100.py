import talib


def calculate_macd_plus_ema100(
    df, fast_length=12, slow_length=26, signal_length=9, ema=100
):
    df["MACD"], df["Signal"], df["Histogram"] = talib.MACD(
        df["close"],
        fastperiod=fast_length,
        slowperiod=slow_length,
        signalperiod=signal_length,
    )
    df["EMA100"] = talib.EMA(df["close"], timeperiod=ema)

    return df


def check_signals_macd_plus_ema100(df, ema_length_up=0.3, ema_length_down=0.3):
    df = df.copy()
    last_row = df.iloc[-1]
    prev_row = df.iloc[-2]

    price_above_ema = last_row["close"] > last_row["EMA100"] * (1 + ema_length_up / 100)
    price_below_ema = last_row["close"] < last_row["EMA100"] * (
        1 - ema_length_down / 100
    )
    if prev_row["Histogram"] < 0 and last_row["Histogram"] >= 0 and price_above_ema:
        return "BUY", last_row

    if prev_row["Histogram"] > 0 and last_row["Histogram"] <= 0 and price_below_ema:
        return "SELL", last_row

    # Si no hay señal, mantener
    return "HOLD", last_row
