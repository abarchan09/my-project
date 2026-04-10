import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

path_1 = r"C:\Users\chaml\Documents\code\bachelorarbeit-mohamed\results\total.csv"
path_2=r"C:\Users\chaml\Documents\code\bachelorarbeit-mohamed\results\total_max_100.csv"

df_1 = pd.read_csv(path_1)
system = df_1["spf_system"].values
df_2=pd.read_csv(path_2)
system= df_2["spf_system"].values
# Zeilen auswählen
df = df_1.loc[0:4].copy()
df =df_2.loc[0:4].copy()

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
ax.set_xlim(1,150)
ax.legend()

# Werte auf Balken schreiben
for i, v in enumerate(hp):
    ax.text(v + 0.001, y[i] - h/2, f"{v:.2f}", va="center")

for i, v in enumerate(system):
    ax.text(v + 0.001, y[i] + h/2, f"{v:.2f}", va="center")

plt.tight_layout()
plt.savefig("lcoh_vergleich.svg", bbox_inches="tight")
plt.show()