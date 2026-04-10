import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

el_path = r"C:\Users\chaml\Documents\code\bachelorarbeit-mohamed\daten\input_data_25.csv"

df_el = pd.read_csv(el_path)

# Zeit korrekt setzen
df_el["time"] = pd.to_datetime(df_el["time"])
df_el = df_el.set_index("time").sort_index()

# Werte in ct/kWh
el_price = df_el["el_price_eur_kwh"] * 100
gas_price = df_el["gas_price"] * 100

plt.figure(figsize=(12,4))

# 🔥 Gaspreis als Fläche (transparent)
plt.fill_between(
    df_el.index,
    gas_price,
    color="green",
    alpha=0.3,
    label="Gaspreis"
)

# 🔥 Strompreis als Linie (oben sichtbar)
plt.plot(
    df_el.index,
    el_price,
    color="blue",
    linewidth=1,
    label="Strompreis"
)

# Achsen & Layout
plt.ylabel("Preis [ct/kWh]")
plt.xlabel("Zeit")

# Monate anzeigen (optional aber empfohlen)
plt.gca().xaxis.set_major_locator(mdates.MonthLocator())
plt.gca().xaxis.set_major_formatter(mdates.DateFormatter("%b"))

# 🔥 kein Leerraum links
plt.xlim(df_el.index.min(), df_el.index.max())
plt.margins(x=0)

plt.legend()
plt.grid(True, alpha=0.3)

plt.tight_layout()
plt.show()