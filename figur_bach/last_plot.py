import pandas as pd
import matplotlib.pyplot as plt

# ---------------------------
# Dateien laden
# ---------------------------

heat_path = r"C:\Users\chaml\Documents\code\bachelorarbeit-mohamed\daten\input_data_25.csv"
weather_path = r"C:\Users\chaml\Documents\code\bachelorarbeit-mohamed\figur_bach\weather_data.csv"

df_heat = pd.read_csv(heat_path)
df_weather = pd.read_csv(weather_path)

# ---------------------------
# Zeitindex setzen
# ---------------------------

df_heat["time"] = pd.to_datetime(df_heat["time"])
df_weather["time"] = pd.to_datetime(df_weather["time"])

df_heat = df_heat.set_index("time")
df_weather = df_weather.set_index("time")

# ---------------------------
# Einheiten umrechnen
# ---------------------------

# Kelvin -> °C
df_weather["temp_C"] = df_weather["temp_air"] - 273.15

# J/m²h -> W/m²
df_weather["ghi_Wm2"] = df_weather["ghi"] / 3600

# ---------------------------
# Plot Style
# ---------------------------

plt.style.use("seaborn-v0_8-whitegrid")

# ---------------------------
# 1 Temperaturplot
# ---------------------------

plt.figure(figsize=(10,4))

df_weather["temp_C"].plot(
    linewidth=1.2
)

plt.ylabel("Außentemperatur [°C]")
plt.xlabel("Zeit")
plt.title("Jahresverlauf der Außentemperatur am Standort Jülich")
plt.tight_layout()
plt.show()


# ---------------------------
# 2 Solarstrahlung
# ---------------------------

plt.figure(figsize=(10,4))

df_weather["ghi_Wm2"].plot(
    linewidth=1.2,
    color="orange"
)

plt.ylabel("Globalstrahlung [W/m²]")
plt.xlabel("Zeit")
plt.title("Globalstrahlung im Jahresverlauf")
plt.tight_layout()
plt.show()


# ---------------------------
# 3 Wärmebedarf
# ---------------------------

plt.figure(figsize=(10,4))

df_heat["heat_demand_kw"].plot(
    linewidth=1.2,
    color="red"
)

plt.ylabel("Wärmeleistung [kW]")
plt.xlabel("Zeit")
plt.title("Wärmebedarf des Hochschulgebäudes")
plt.tight_layout()
plt.show()
