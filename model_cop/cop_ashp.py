import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates


def cop_from_outdoor_temperature(
    T_air,
    T_ref=None,
    COP_ref=None,
    cop_min=1.5,
    cop_max=5.0,
    clamp=True,
    fill_method="ffill_bfill",
):
    """
    Berechnet einen temperaturabhängigen COP für eine ASHP
    auf Basis der Außentemperatur.
    """

    if T_ref is None:
        T_ref = np.array([-15, -7, 2, 7, 10, 15, 20,30], dtype=float)
    else:
        T_ref = np.array(T_ref, dtype=float)

    if COP_ref is None:
        COP_ref = np.array([1.8, 2.1, 2.4, 2.7, 2.8, 3.0, 3.2,5], dtype=float)
    else:
        COP_ref = np.array(COP_ref, dtype=float)

    if T_ref.shape != COP_ref.shape:
        raise ValueError("T_ref and COP_ref must have the same length.")

    if not isinstance(T_air, pd.Series):
        T_air = pd.Series(T_air)

    T_air = pd.to_numeric(T_air, errors="coerce")
    T_air = T_air.replace([np.inf, -np.inf], np.nan)

    if fill_method == "ffill_bfill":
        T_air = T_air.ffill().bfill()
    elif fill_method == "interpolate":
        T_air = T_air.interpolate(limit_direction="both")
    elif fill_method is None:
        pass
    else:
        raise ValueError("fill_method must be 'ffill_bfill', 'interpolate', or None.")

    if T_air.isna().any():
        raise ValueError("T_air still contains NaNs after cleaning.")

    T_vals = T_air.values.astype(float)

    if clamp:
        T_vals = np.clip(T_vals, T_ref.min(), T_ref.max())

    cop_values = np.interp(T_vals, T_ref, COP_ref)
    cop_values = np.clip(cop_values, cop_min, cop_max)

    return pd.Series(cop_values, index=T_air.index, name="COP")

def calculate_cop_ashp(weather_path):
    """
    Lädt Wetterdaten und berechnet die COP-Zeitreihe der ASHP.
    Erwartet eine Spalte 'time' und 'temp_air' in Kelvin.
    """
    df_weather = pd.read_csv(weather_path, parse_dates=["time"])
    df_weather = df_weather.set_index("time")

    # Kelvin -> °C
    T_air = df_weather["temp_air"] - 273.15

    cop_t = cop_from_outdoor_temperature(T_air)
    return cop_t




