import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# Pfade
path_1 = r"C:\Users\chaml\Documents\code\bachelorarbeit-mohamed\results\performance_ASHP.csv"
path_2 = r"C:\Users\chaml\Documents\code\bachelorarbeit-mohamed\results\performance_GSHP.csv"
path_3 = r"C:\Users\chaml\Documents\code\bachelorarbeit-mohamed\results\performance_SA-WSHP.csv"

# Einlesen
df1 = pd.read_csv(path_1).set_index("scenario")
df2 = pd.read_csv(path_2).set_index("scenario")
df3 = pd.read_csv(path_3).set_index("scenario")

df = pd.concat([df1, df2, df3])

# 👉 Index ändern
df.index = ["S1", "S2", "S3"]

# Werte extrahieren
hp = df["spf_hp"]
system = df["spf_system"]

# Szenarien
scenarios = df.index

# Positionen
y = np.arange(len(scenarios))
h = 0.35

# Plot
fig, ax = plt.subplots(figsize=(8, 4.5))

ax.barh(y - h/2, hp, height=h, label="SPF$_{HP}$")
ax.barh(y + h/2, system, height=h, label="SPF$_{System}$")

ax.set_yticks(y)
ax.set_yticklabels(scenarios)

ax.set_xlabel("SPF [-]")
ax.set_title("Vergleich der Seasonal Performance Factors (SPF) der Wärmepumpe und des Gesamtsystems")

ax.legend()

# Werte anzeigen
for i, v in enumerate(hp):
    ax.text(v + 0.02, y[i] - h/2, f"{v:.1f}", va="center")

for i, v in enumerate(system):
    ax.text(v + 0.02, y[i] + h/2, f"{v:.1f}", va="center")

plt.tight_layout()
plt.savefig("spf_vergleich.svg", bbox_inches="tight")
plt.show()