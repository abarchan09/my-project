import pandas as pd
import matplotlib.pyplot as plt

# Pfad
path = r"C:\Users\chaml\Documents\code\bachelorarbeit-mohamed\results\summary_neu_SA-WSHP.csv"

# CSV laden
df = pd.read_csv(path)

# Index setzen
df = df.set_index("scenario")

# Szenario S3 auswählen
s3 = df.loc["SA-WSHP"]

# =========================
# Speicherwerte extrahieren
# (Spaltennamen ggf. anpassen!)
# =========================
solar_to_storage= s3["solar_to_storage_kWh"]/1000 
storage_charge= s3["storage_charge_kWh"]/1000
storage_to_environmental_heat = s3["storage_to_environmental_heat_kWh"] / 1000
verluste= solar_to_storage-storage_to_environmental_heat


#Daten für Plot
labels = ["Beladung", "Entladung","Verluste"]
values = [solar_to_storage,  storage_to_environmental_heat,verluste]

# =========================
# Plot
# =========================
fig, ax = plt.subplots(figsize=(6, 4))

ax.bar(labels, values, edgecolor="black")

#Werte anzeigen
for i, v in enumerate(values):
    ax.text(i, v + 0.02 * max(values), f"{v:.1f}", ha="center")

ax.set_ylabel("Energie [MWh]")
ax.set_title("Speichernutzung im Szenario S3")


ax.grid(axis="y", linestyle="--", alpha=0.6)

plt.tight_layout()
#plt.savefig("speicher_S3.svg", bbox_inches="tight")
plt.show()