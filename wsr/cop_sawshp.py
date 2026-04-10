import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.patches as mpatches

def calculate_cop_sawshp(
    weather_path: str,
    ghi_col: str = "ghi",
    time_col: str = "time",
    eta_coll: float = 0.37,         # [-]
    A_coll: float = 500.0,          # [m²]
    Q_verlust: float = 70.8,        # [W]
    m_dot: float = 6.0,             # [kg/s]
    cp: float = 4180.0,             # [J/(kg K)]
    T_gw: float = 10.0,             # [°C]
    T_senk: float = 55.0,           # [°C]
    eta_carnot: float = 0.5,        # [-]
    T_source_min: float = 0.0,      # [°C]
    T_source_max: float = 15.0,     # [°C]
    cop_min: float = 1.0,           # [-]
    cop_max: float = 5.0            # [-]
) -> pd.DataFrame:

    if not os.path.exists(weather_path):
        raise FileNotFoundError(f"Wetterdatei nicht gefunden: {weather_path}")

    df = pd.read_csv(weather_path)

    if time_col not in df.columns:
        raise KeyError(f"Zeitspalte '{time_col}' nicht in Wetterdatei vorhanden.")
    if ghi_col not in df.columns:
        raise KeyError(f"GHI-Spalte '{ghi_col}' nicht in Wetterdatei vorhanden.")
    if "temp_air" not in df.columns:
        raise KeyError("Spalte 'temp_air' nicht in der Wetterdatei vorhanden.")

    # Zeitstempel
    df[time_col] = pd.to_datetime(df[time_col], errors="coerce")
    if df[time_col].isna().any():
        n_bad = df[time_col].isna().sum()
        raise ValueError(f"{n_bad} ungültige Zeitwerte in Wetterdatei gefunden.")

    df = df.set_index(time_col).sort_index()

    # GHI bereinigen
    ghi_raw = pd.to_numeric(df[ghi_col], errors="coerce")
    ghi_raw = ghi_raw.replace([np.inf, -np.inf], np.nan)
    ghi_raw = ghi_raw.interpolate(limit_direction="both").ffill().bfill()

    if ghi_raw.isna().any():
        raise ValueError("GHI enthält nach Bereinigung weiterhin NaN-Werte.")

    df["GHI"] = (ghi_raw / 3600.0).clip(lower=0.0)  # [W/m²]

    # temp_air bereinigen
    df["temp_air"] = pd.to_numeric(df["temp_air"], errors="coerce")
    df["temp_air"] = df["temp_air"].interpolate(limit_direction="both").ffill().bfill()

    # Falls Kelvin, dann in °C umrechnen
    if df["temp_air"].mean() > 100:
        df["temp_air"] = df["temp_air"] - 273.15

    # Solarleistung
    df["Q_solar"] = A_coll * df["GHI"] * eta_coll
    df["Q_solar_kW"] = df["Q_solar"] / 1000.0

    # Quellentemperatur
    df["T_source"] = T_gw + (df["Q_solar"] - Q_verlust) / (m_dot * cp)
    df["T_source"] = df["T_source"].clip(lower=T_source_min, upper=T_source_max)

    # COP
    T_source_K = df["T_source"] + 273.15
    T_senk_K = T_senk + 273.15
    delta_T = (T_senk_K - T_source_K).clip(lower=1e-6)

    df["cop_s_3"] = eta_carnot * (T_senk_K / delta_T)
    df["cop_s_3"] = df["cop_s_3"].replace([np.inf, -np.inf], np.nan)
    df["cop_s_3"] = df["cop_s_3"].interpolate(limit_direction="both").ffill().bfill()
    df["cop_s_3"] = df["cop_s_3"].clip(lower=cop_min, upper=cop_max)

    print(f"Maximale Quellentemperatur: {df['T_source'].max():.2f} °C")
    print(f"Zeitpunkt des Maximums: {df['T_source'].idxmax()}")

    return df


def plot_cop_sawshp_with_heating_period(
    df_results,
    T_gw=10.0,
    T_source_max=15.0,
    daily_mean=True
):
    """
    Plot von Quellentemperatur und COP über das Jahr.
    Die Heizperiode wird fest definiert als:
    - 01.01 bis 15.05
    - 15.09 bis 31.12
    """

    if not isinstance(df_results.index, pd.DatetimeIndex):
        raise ValueError("Der Index von df_results muss ein DatetimeIndex sein.")

    df_plot = df_results[["T_source", "cop_s_3"]].copy()

    if daily_mean:
        df_plot = df_plot.resample("D").mean()
    df_plot = df_plot.dropna()
    fig, ax1 = plt.subplots(figsize=(12, 5))

    # Heizperioden farbig markieren
    years = sorted(df_plot.index.year.unique())

    for year in years:
        start_1 = pd.Timestamp(f"{year}-01-01")
        end_1 = pd.Timestamp(f"{year}-05-15")
        start_2 = pd.Timestamp(f"{year}-09-15")
        end_2 = pd.Timestamp(f"{year}-12-31")

        ax1.axvspan(start_1, end_1, color="red", alpha=0.15, zorder=0)
        ax1.axvspan(start_2, end_2, color="red", alpha=0.15, zorder=0)

    # Temperatur links
    ax1.plot(
        df_plot.index,
        df_plot["T_source"],
        color="red",
        linewidth=1.5,
        label="Quellentemperatur"
    )
    ax1.axhline(
        T_gw,
        color="gray",
        linestyle="--",
        linewidth=1,
        label=f"Brunnenwasser ({T_gw:.0f} °C)"
    )
    ax1.axhline(
        T_source_max,
        color="black",
        linestyle=":",
        linewidth=1,
        label=f"Obergrenze ({T_source_max:.0f} °C)"
    )
    ax1.set_xlabel("Zeit")
    ax1.set_ylabel("Temperatur in °C")
    ax1.grid(True)

    # COP rechts
    ax2 = ax1.twinx()
    ax2.plot(
        df_plot.index,
        df_plot["cop_s_3"],
        color="blue",
        linewidth=1.5,
        label="COP"
    )
    ax2.set_ylabel("COP (-)")

    # Monatsachse
    ax1.xaxis.set_major_locator(mdates.MonthLocator())
    ax1.xaxis.set_major_formatter(mdates.DateFormatter("%b"))

    # Legende erweitern
    heating_patch = mpatches.Patch(color="red", alpha=0.15, label="Heizperiode")

    lines = ax1.get_lines() + ax2.get_lines()
    labels = [line.get_label() for line in lines]

    lines.append(heating_patch)
    labels.append("Heizperiode")

    ax1.legend(lines, labels, loc="upper right")
    ax1.set_xlim(df_plot.index.min(), df_plot.index.max())
    plt.margins(x=0) 
    plt.title("Zeitabhängiger COP der SA-WSHP")
    plt.tight_layout()
    plt.savefig(
        r"C:\Users\chaml\Documents\code\bachelorarbeit-mohamed\Png\cop_sawshp_heizperiode.svg",
        format="svg",
        bbox_inches="tight"
    )

    plt.show()
    

if __name__ == "__main__":
    weather_path = r"C:\Users\chaml\OneDrive\Documents\datenbank\daten\daten_quelle\wetter\weather_data.csv"

    df_results = calculate_cop_sawshp(
        weather_path=weather_path,
        A_coll=500.0,
        m_dot=6.0,
        T_gw=10.0,
        T_senk=55.0
    )

    plot_cop_sawshp_with_heating_period(
        df_results,
        T_gw=10.0,
        T_source_max=15.0,
        daily_mean=True
    )
   