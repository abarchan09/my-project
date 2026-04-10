import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

path = r"C:\Users\chaml\Documents\code\bachelorarbeit-mohamed\results\summary.csv"

# CSV laden
df = pd.read_csv(path)
df = df.set_index("scenario")

# Daten in MWh
grid_import = df["grid_import_el_kWh"] / 1000
pv_gen = df["pv_generation_kWh"] / 1000
grid_export = df["grid_export_el_kWh"] / 1000

# PV-Eigenverbrauch
pv_self = pv_gen - grid_export

# Gesamtstrombedarf Wärmepumpe
total_el = grid_import + pv_self

# Anteil PV [%]
pv_share = (pv_self / total_el) * 100
grid_share = (grid_import / total_el) * 100
# Positionen
x = np.arange(len(df.index))

# =========================
# Plot (Stacked Bars!)
# =========================
fig, ax = plt.subplots(figsize=(8, 4.5))

# gestapelte Balken
ax.bar(x, grid_import, label="Netzstrombezug", edgecolor="black")
ax.bar(x, pv_self, bottom=grid_import, label="PV-Anteil", edgecolor="black")

# Prozentwerte oben anzeigen
for i in range(len(x)):
    # Netzstrom (unten)
    ax.text(
        x[i],
        grid_import[i] / 2,
        f"{grid_share[i]:.1f}%",
        ha="center",
        va="center",
        fontsize=10,
        color="white"
    )

    # PV (oben)
    ax.text(
        x[i],
        grid_import[i] + pv_self[i] / 2,
        f"{pv_share[i]:.1f}%",
        ha="center",
        va="center",
        fontsize=10,
        color="white"   # besser sichtbar auf blau
    )

# Achsen
ax.set_xticks(x)
ax.set_xticklabels(df.index)

ax.set_ylabel("Elektrische Energie [MWh]")
ax.set_title("Deckung des Strombedarfs der Wärmepumpe durch PV und Netzstrom")
ax.legend()
ax.grid(axis="y", linestyle="--", alpha=0.6)

plt.tight_layout()
plt.savefig("pv_anteil_wp.png", dpi=300, bbox_inches="tight")
