import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
path=r"C:\Users\chaml\Documents\code\bachelorarbeit-mohamed\figur_bach\weather_data.csv"
df = pd.read_csv(path)

# Zeitspalte sicher in datetime umwandeln
df["time"] = pd.to_datetime(df["time"], errors="coerce")

# ungültige Zeilen entfernen
df = df.dropna(subset=["time", "ghi", "temp_air"])

# Index setzen
df = df.set_index("time").sort_index()

print(df.index.shape)        # sollte z. B. (8736,) sein
print(df["ghi"].shape)       # sollte gleich lang sein
print(df["temp_air"].shape)  # sollte gleich lang sein

fig, axes = plt.subplots(2, 1, figsize=(12, 6), sharex=True)

axes[0].plot(df.index, df["ghi"]/3600,color= "red", linewidth=0.8)
axes[0].set_ylabel("Globalstrahlung (W/m²)")
axes[0].legend(loc="upper right", frameon=False)
axes[0].grid(True, alpha=0.3)

axes[1].plot(df.index, df["temp_air"], linewidth=0.8)
axes[1].set_ylabel("Außentemperatur (°C)")
axes[1].set_xlabel("Zeit")
axes[1].legend(loc="upper right", frameon=False)
axes[1].grid(True, alpha=0.3)



# Monatsnamen
axes[1].xaxis.set_major_locator(mdates.MonthLocator())
axes[1].xaxis.set_major_formatter(mdates.DateFormatter("%b"))

start = df.index.min().replace(day=1, hour=0)
end = df.index.max()
axes[1].set_xlim(start, end)

# kein Leerraum links/rechts
for ax in axes:
    ax.margins(x=0)

plt.tight_layout()
plt.show()