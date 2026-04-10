import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

path = r"C:\Users\chaml\Documents\code\bachelorarbeit-mohamed\results\totat.csv"

df = pd.read_csv(path)

# Zeilen auswählen
df = df.loc[0:4].copy()

# Namen für die Achse
scenarios = ["S1", "S2","S3"]
# Daten
hp = df["lcoh_hp_eur_per_kwh"].values*100
system = df["lcoh_system_eur_per_kwh"].values*100


# Positionen
y = np.arange(len(scenarios))
h = 0.35

fig, ax = plt.subplots(figsize=(8, 4.5))

ax.barh(y - h/2, hp, height=h, label="LCOH$_{HP}$")
ax.barh(y + h/2, system, height=h, label="LCOH$_{System}$")

ax.set_yticks(y)
ax.set_yticklabels(scenarios)

ax.set_xlabel("LCOH [cent/kWh]")
ax.set_title("Vergleich von LCOH der Wärmepumpe und Gesamtsystem")
ax.set_xlim(1,16)
ax.legend()

# Werte auf Balken schreiben
for i, v in enumerate(hp):
    ax.text(v + 0.001, y[i] - h/2, f"{v:.2f}", va="center")

for i, v in enumerate(system):
    ax.text(v + 0.001, y[i] + h/2, f"{v:.2f}", va="center")

plt.tight_layout()
plt.savefig("lcoh_vergleich.svg", bbox_inches="tight")
plt.show()