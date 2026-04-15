import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

path_1 = r"C:\Users\chaml\Documents\code\bachelorarbeit-mohamed\results\total.csv"
path_2 = r"C:\Users\chaml\Documents\code\bachelorarbeit-mohamed\results\total_max_100.csv"

# Daten lesen
df_1 = pd.read_csv(path_1)
df_2 = pd.read_csv(path_2)

# Nur S1 bis S3
df_1 = df_1.loc[0:2].copy()
df_2 = df_2.loc[0:2].copy()

# Szenarien
szenarien = ["S1", "S2", "S3"]

# LCOH System [ct/kWh]
system_oemof = df_1["lcoh_system_eur_per_kwh"].values * 100
system_100kw = df_2["lcoh_system_eur_per_kwh"].values * 100

# LCOH HP [ct/kWh]
hp_oemof = df_1["lcoh_hp_eur_per_kwh"].values * 100
hp_100kw = df_2["lcoh_hp_eur_per_kwh"].values * 100

# Prozentuale Änderung
delta_hp = (hp_oemof - hp_100kw) / hp_oemof * 100
delta_sys = (system_oemof - system_100kw) / system_oemof * 100

x = np.arange(len(szenarien))
width = 0.35

# Figure
fig, axes = plt.subplots(1, 2, figsize=(12, 5), sharey=True)

# -------------------------
# (a) HP
# -------------------------
ax1 = axes[0]
ax1.bar(
    x - width/2, hp_oemof, width,
    label=r"LCOH$_{HP}$ ohne Begrenzung"
)
ax1.bar(
    x + width/2, hp_100kw, width,
    label=r"LCOH$_{HP}$ mit 100 kW"
)

for i in range(len(x)):
    ax1.text(
        x[i],
        max(hp_oemof[i], hp_100kw[i]) + 0.3,
        f"{delta_hp[i]:+.1f}%",
        ha="center",
        va="bottom",
        fontsize=10
    )

ax1.set_xticks(x)
ax1.set_xticklabels(szenarien)
ax1.set_ylabel("LCOH [ct/kWh]")
ax1.set_title("Wärmepumpe")
ax1.set_ylim(0, 13)
ax1.grid(axis="y", linestyle="--", alpha=0.6)
ax1.legend(frameon=False)

# -------------------------
# (b) System
# -------------------------
ax2 = axes[1]
ax2.bar(
    x - width/2, system_oemof, width,
    label=r"LCOH$_{System}$ ohne Begrenzung"
)
ax2.bar(
    x + width/2, system_100kw, width,
    label=r"LCOH$_{System}$ mit 100 kW"
)

for i in range(len(x)):
    ax2.text(
        x[i],
        max(system_oemof[i], system_100kw[i]) + 0.3,
        f"{delta_sys[i]:+.1f}%",
        ha="center",
        va="bottom",
        fontsize=10
    )

ax2.set_xticks(x)
ax2.set_xticklabels(szenarien)
ax2.set_title("Gesamtsystem")
ax2.set_ylim(0, 13)
ax2.grid(axis="y", linestyle="--", alpha=0.6)
ax2.legend(frameon=False)

plt.tight_layout()
plt.savefig("lcoh_vergleich_wissenschaftlich.svg", dpi=300, bbox_inches="tight")
plt.show()