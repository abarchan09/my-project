import matplotlib.pyplot as plt
import numpy as np

# Daten
Szenarien = ["S1", "S2", "S3"]

# HP
lcoh_hp = np.array([7.6, 7.4, 14.0])
lcoh_oemof_hp = np.array([9.8, 9.5, 14.0])

# System
lcoh_sys = np.array([8.8, 8.7, 11.0])
lcoh_oemof_sys = np.array([7.8, 7.1, 11.0])

# Prozentänderung
delta_hp = (lcoh_oemof_hp - lcoh_hp) / lcoh_hp * 100
delta_sys = (lcoh_oemof_sys - lcoh_sys) / lcoh_sys * 100

x = np.arange(len(Szenarien))
width = 0.35

# Farben


# Figure
fig, axes = plt.subplots(1, 2, figsize=(12, 5), sharey=True)

# -------------------------
# (a) HP
# -------------------------
ax1 = axes[0]
ax1.bar(
    x - width/2, lcoh_hp, width,
    label=r"LCOH$_{HP}$ vor oemof",
    
)
ax1.bar(
    x + width/2, lcoh_oemof_hp, width,
    label=r"LCOH$_{HP}$ nach oemof",
    
)

for i in range(len(x)):
    ax1.text(
        x[i],
        max(lcoh_hp[i], lcoh_oemof_hp[i]) + 0.35,
        f"{delta_hp[i]:+.1f}%",
        ha="center",
        va="bottom",
        fontsize=10
    )

ax1.set_xticks(x)
ax1.set_xticklabels(Szenarien)
ax1.set_ylabel("LCOH [ct/kWh]")
ax1.set_title(" Wärmepumpe")
ax1.set_ylim(0, 16)
ax1.grid(axis="y", linestyle="--", alpha=0.6)
ax1.legend(frameon=False)

# -------------------------
# (b) System
# -------------------------
ax2 = axes[1]
ax2.bar(
    x - width/2, lcoh_sys, width,
    label=r"LCOH$_{System}$ vor oemof",
    
)
ax2.bar(
    x + width/2, lcoh_oemof_sys, width,
    label=r"LCOH$_{System}$ nach oemof",
    
)

for i in range(len(x)):
    ax2.text(
        x[i],
        max(lcoh_sys[i], lcoh_oemof_sys[i]) + 0.35,
        f"{delta_sys[i]:+.1f}%",
        ha="center",
        va="bottom",
        fontsize=10
    )

ax2.set_xticks(x)
ax2.set_xticklabels(Szenarien)
ax2.set_title("Gesamtsystem")
ax2.set_ylim(0, 16)
ax2.grid(axis="y", linestyle="--", alpha=0.6)
ax2.legend(frameon=False)

plt.tight_layout()

plt.savefig("lcoh_vergleich_wissenschaftlich.svg", dpi=300, bbox_inches="tight")
plt.show()


