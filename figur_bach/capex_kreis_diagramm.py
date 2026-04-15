import matplotlib.pyplot as plt

# Labels (nur für Legende!)
labels = [
    "Installation",
    "Anlagenkomponenten",
    "Zusätzliche Kosten"
]

# KORREKTE Daten (ohne doppelte Zählung!)
values_a = [1080*0.9, 1080*0.1, 470]
values_wasser = [460*0.9, 460*0.1, 550]
values_erd = [640*0.9, 640*0.1, 2130]

# Subplots
fig, axs = plt.subplots(1, 3, figsize=(12, 4))

# ASHP
wedges1, _, _ = axs[0].pie(values_a, autopct='%1.1f%%', startangle=90)
axs[0].set_title("ASHP")

# WSHP
wedges2, _, _ = axs[1].pie(values_wasser, autopct='%1.1f%%', startangle=90)
axs[1].set_title("WSHP")

# GSHP
wedges3, _, _ = axs[2].pie(values_erd, autopct='%1.1f%%', startangle=90)
axs[2].set_title("GSHP")

# Kreisform
for ax in axs:
    ax.axis('equal')

# 🔥 Gemeinsame Legende (nur einmal!)
fig.legend(
    wedges1,        # Farben übernehmen
    labels,
    loc="lower center",
    ncol=3
)

plt.suptitle("Vergleich der Investitionskostenstruktur")
for ax in axs:
    ax.axis('equal')

fig.legend(wedges1, labels, loc="lower center", ncol=3)

plt.tight_layout()

# 🔥 Export (wichtig!)
plt.savefig("investitionskosten.svg", bbox_inches='tight')

plt.show()
