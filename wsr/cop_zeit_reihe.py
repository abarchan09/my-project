import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


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
        T_ref = np.array([-15, -7, 2, 7, 10, 15, 20], dtype=float)
    else:
        T_ref = np.array(T_ref, dtype=float)

    if COP_ref is None:
        COP_ref = np.array([1.8, 2.1, 2.4, 2.7, 2.8, 3.0, 3.2], dtype=float)
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





# ============================================================
# Dateien
# ============================================================

weather_path = r"C:\Users\chaml\OneDrive\Documents\datenbank\daten\daten_quelle\wetter\weather_data.csv"
input_data_path = r"C:\Users\chaml\Documents\code\bachelorarbeit-mohamed\daten\input_data_25.csv"

# ============================================================
# Wetterdaten laden und COP berechnen
# ============================================================

df_weather = pd.read_csv(weather_path, parse_dates=["time"])
df_weather = df_weather.set_index("time")

# temp_air in Kelvin -> °C
T_air = df_weather["temp_air"] - 273.15

cop_t = cop_from_outdoor_temperature(T_air)

# ============================================================
# Plot
# ============================================================
def plot_cop_heating_period(cop_series, t_series, T_thresh=20, daily_mean=True):
    """
    Plot nur für Heizperiode (T_air < T_thresh).
    """
    if not isinstance(cop_series.index, pd.DatetimeIndex):
        raise ValueError("Index must be DatetimeIndex")

    mask = t_series < T_thresh
    cop_hp = cop_series[mask]

    if daily_mean:
        cop_hp = cop_hp.resample("D").mean()

    plt.figure(figsize=(10, 4))
    plt.plot(cop_hp.index, cop_hp, linewidth=1.0)
    plt.xlabel("Zeit")
    plt.ylabel("COP (-)")
    plt.title(f"COP in der Heizperiode (T < {T_thresh} °C)")
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.show()


plt.figure(figsize=(12, 4))
plt.plot(cop_t.index, cop_t, linewidth=0.8)
plt.ylabel("COP [-]")
plt.xlabel("Zeit")
plt.title("Zeitabhängiger COP der ASHP")
plt.grid(alpha=0.3)
plt.tight_layout()
plt.show()

# ============================================================
# COP in input_data_25.csv einfügen
# ============================================================

#df_input = pd.read_csv(input_data_path, parse_dates=["time"])
#df_input = df_input.set_index("time")

# COP auf denselben Zeitindex bringen
#df_input["COP"] = cop_t.reindex(df_input.index)

# falls NaNs durch Indexabweichung entstehen
#df_input["COP"] = df_input["COP"].ffill().bfill()

# wieder speichern
#df_input.reset_index().to_csv(input_data_path, index=False, encoding="utf-8-sig")

#print(f"COP erfolgreich als Spalte 'COP' in {input_data_path} gespeichert.")

