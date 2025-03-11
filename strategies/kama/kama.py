import pandas as pd
import numpy as np

import pandas as pd
import numpy as np


import pandas as pd
import numpy as np


def kaufman_adaptive_moving_average(df, length=14, fast_length=2, slow_length=30):
    df = df.copy()  # Evitar modificar el DataFrame original
    src = df["close"]

    # Paso 1: Calcular Momento (MOM)
    mom = abs(src.diff(length))
    print("Momento (mom):")
    print(mom.tail(10))

    # Paso 2: Calcular Volatilidad
    volatility = src.diff().abs().rolling(length).sum()
    print("Volatilidad (volatility):")
    print(volatility.tail(10))

    # Paso 3: Calcular Ratio de Eficiencia (ER)
    er = np.where(
        volatility != 0, mom / volatility, np.nan
    )  # Si volatility es 0, evitar división por 0
    print("Eficiencia (ER):")
    print(er[-10:])  # Mostrar los últimos 10 valores

    # Paso 4: Calcular Alpha
    fast_alpha = 2 / (fast_length + 1)
    slow_alpha = 2 / (slow_length + 1)
    alpha = (er * (fast_alpha - slow_alpha) + slow_alpha) ** 2
    print("Alpha:")
    print(alpha[-10:])

    # Paso 5: Calcular KAMA
    kama = np.zeros(len(df))
    first_valid_index = np.where(~np.isnan(alpha))[0][
        0
    ]  # Buscar el primer índice válido de alpha

    if np.isnan(first_valid_index):  # Si no hay valores válidos, salir
        print("Error: No hay suficientes datos para calcular KAMA.")
        df["KAMA"] = np.nan
        return df

    kama[first_valid_index] = src.iloc[first_valid_index]  # Asignar primer valor válido
    for i in range(first_valid_index + 1, len(df)):
        kama[i] = alpha[i] * src.iloc[i] + (1 - alpha[i]) * kama[i - 1]

    df["KAMA"] = kama
    return df


def check_signals_kama(df):
    df = kaufman_adaptive_moving_average(df)

    if df["KAMA"].isna().sum() == len(df):
        print("Error: No se pudo calcular el KAMA correctamente.")
        return "HOLD", None

    last_row = df.iloc[-1]
    prev_row = df.iloc[-2]

    # Señales de compra y venta basadas en el cambio de dirección del KAMA
    if last_row["KAMA"] > prev_row["KAMA"]:
        return "BUY", last_row
    elif last_row["KAMA"] < prev_row["KAMA"]:
        return "SELL", last_row

    return "HOLD", last_row
