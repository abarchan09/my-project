import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# Pfade
path_1 = r"C:\Users\chaml\Documents\code\bachelorarbeit-mohamed\results\summary_neu_ASHP.csv"
path_2 = r"C:\Users\chaml\Documents\code\bachelorarbeit-mohamed\results\summary_neu_GSHP.csv"
path_3 = r"C:\Users\chaml\Documents\code\bachelorarbeit-mohamed\results\summary_neu_SA-WSHP.csv"

# Dateien einlesen
df1 = pd.read_csv(path_1)
df2 = pd.read_csv(path_2)
df3 = pd.read_csv(path_3)

# Jeweils Szenario setzen
df1 = df1.set_index("scenario")
df2 = df2.set_index("scenario")
df3 = df3.set_index("scenario")

# Gewünschte Szenarien aus den drei Originalquellen holen
# Passe die Indexnamen an, falls sie in den CSV anders heißen
s1 = df1.loc["ASHP"]
s2 = df2.loc["GSHP"]
s3 = df3.loc["SA-WSHP"]

# Neue gemeinsame Tabelle aufbauen
df = pd.DataFrame(
    [s1, s2, s3],
    index=["ASHP", "GSHP", "SA-WSHP"]
)

# Daten in MWh
grid_import = df["grid_import_el_kWh"] / 1000
pv_gen = df["pv_generation_kWh"] / 1000
grid_export = df["grid_export_el_kWh"] / 1000

# PV-Eigenverbrauch
pv_self = (pv_gen - grid_export).clip(lower=0)

# Gesamtstrombedarf der Wärmepumpe
total_el = grid_import + pv_self

# Prozentanteile
pv_share = (pv_self / total_el * 100).fillna(0)
grid_share = (grid_import / total_el * 100).fillna(0)

# x-Positionen
x = np.arange(len(df.index))

# Plot
fig, ax = plt.subplots(figsize=(8, 4.5))

ax.bar(x, grid_import, label="Netzstrombezug", edgecolor="black")
ax.bar(x, pv_self, bottom=grid_import, label="PV-Anteil", edgecolor="black")

# Prozentwerte in die Balken schreiben
for i, scen in enumerate(df.index):

    # ❌ Netzanteil NICHT anzeigen bei S3
    if scen != "SA-WSHP":
        if grid_import.iloc[i] > 0:
            ax.text(
                x[i],
                grid_import.iloc[i] / 2,
                f"{grid_share.iloc[i]:.1f}%",
                ha="center",
                va="center",
                fontsize=10,
                color="black"
            )

    # ✅ PV-Anteil IMMER anzeigen (auch bei S3)
    if pv_self.iloc[i] > 0:
        ax.text(
            x[i],
            grid_import.iloc[i] + pv_self.iloc[i] / 2,
            f"{pv_share.iloc[i]:.1f}%",
            ha="center",
            va="center",
            fontsize=10,
            color="black"
        )

ax.set_xticks(x)
ax.set_xticklabels(df.index)
ax.set_ylabel("Elektrische Energie [MWh]")
ax.set_title("Deckung des Strombedarfs der Wärmepumpe durch PV und Netzstrom")
ax.legend()
ax.grid(axis="y", linestyle="--", alpha=0.6)

plt.tight_layout()
plt.savefig("pv_anteil_wp.png", dpi=300, bbox_inches="tight")
plt.show()