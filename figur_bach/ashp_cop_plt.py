import pandas as pd
import matplotlib.pyplot as plt

# ---------------------------
# Dateien laden
# ---------------------------

heat_path = r"C:\Users\chaml\Documents\code\bachelorarbeit-mohamed\daten\input_data_25.csv"
weather_path = r"C:\Users\chaml\Documents\code\bachelorarbeit-mohamed\figur_bach\weather_data.csv"

df_cop = pd.read_csv(heat_path)
df_weather = pd.read_csv(weather_path)

# ---------------------------
# Zeitspalte setzen
# ---------------------------

df_cop["time"] = pd.to_datetime(df_cop["time"])
df_weather["time"] = pd.to_datetime(df_weather["time"])

df_cop = df_cop.set_index("time")
df_weather = df_weather.set_index("time")

# ---------------------------
# Temperatur umrechnen
# ---------------------------

df_weather["temp_C"] = df_weather["temp_air"].astype(float) - 273.15

# ---------------------------
# Daten zusammenführen
# ---------------------------

df = pd.DataFrame(index=df_cop.index)
df["COP"] = pd.to_numeric(df_cop["COP"], errors="coerce")
df["temp_C"] = pd.to_numeric(df_weather["temp_C"], errors="coerce")

# Nur gemeinsame Zeitpunkte behalten
df = df.dropna(subset=["COP", "temp_C"])

# Optional: glätten mit Tagesmittelwerten
df_plot = df.resample("D").mean()

# ---------------------------
# Plot
# ---------------------------

plt.style.use("seaborn-v0_8-whitegrid")

fig, ax1 = plt.subplots(figsize=(10, 4))

# COP
ax1.plot(
    df_plot.index,
    df_plot["COP"],
    color="green",
    linewidth=2,
    label="COP"
)
ax1.set_ylabel("COP [-]", color="green")
ax1.tick_params(axis="y", labelcolor="green")

# zweite y-Achse für Temperatur
ax2 = ax1.twinx()
ax2.plot(
    df_plot.index,
    df_plot["temp_C"],
    color="tab:blue",
    linewidth=2,
    label="Außentemperatur"
)
ax2.set_ylabel("Außentemperatur [°C]", color="tab:blue")
ax2.tick_params(axis="y", labelcolor="tab:blue")

plt.title("Verlauf von COP und Außentemperatur")
ax1.set_xlabel("Zeit")

fig.tight_layout()
plt.show()