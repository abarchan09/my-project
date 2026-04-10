import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

path = r"C:\Users\chaml\Documents\code\bachelorarbeit-mohamed\results\total.csv"

df = pd.read_csv(path)

df = df.loc[0:4].copy()

scenarios = ["S1", "S2", "S3"]

hp = df["spf_hp"].values
system = df["spf_system"].values

y = np.arange(len(scenarios))
h = 0.35

fig, ax = plt.subplots(figsize=(8, 4.5))

ax.barh(y - h/2, hp, height=h, label="SPF$_{HP}$")
ax.barh(y + h/2, system, height=h, label="SPF$_{System}$")

ax.set_yticks(y)
ax.set_yticklabels(scenarios)

ax.set_xlabel("SPF [-]")
ax.set_title("Vergleich der SPF der Wärmepumpe und Gesamtsystem ")

ax.legend()

for i, v in enumerate(hp):
    ax.text(v + 0.02, y[i] - h/2, f"{v:.1f}", va="center")

for i, v in enumerate(system):
    ax.text(v + 0.02, y[i] + h/2, f"{v:.1f}", va="center")

plt.tight_layout()
plt.savefig("spf_vergleich.svg", bbox_inches="tight")
plt.show()