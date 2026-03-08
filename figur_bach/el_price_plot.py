import pandas as pd
import matplotlib.pyplot as plt

el_path = r"C:\Users\chaml\Documents\code\bachelorarbeit-mohamed\daten\input_data_25.csv"

df_el= pd.read_csv(el_path)
df_el["time"] = pd.to_datetime(df_el["time"])
df_el = df_el.set_index("time")

plt.figure(figsize=(12,4))

plt.plot(df_el.index, df_el["el_price_eur_kwh"]*100, color="blue", alpha=0.6)

plt.ylabel("Strompreis [ct/kWh]")
plt.xlabel("Zeit")
plt.title("Zeitlicher Verlauf des Strompreises (Day-Ahead)")

plt.grid(True, alpha=0.3)

plt.tight_layout()
plt.show()