import matplotlib.pyplot as plt

labels = ["Installation", "Komponenten", "Zusätzliche Kosten"]
colors = ["#28B4BC", "#DA5679", "#AFBAB9"]

data = {
    "ASHP": [1080 * 0.9, 1080 * 0.1, 470],
    "WSHP": [460 * 0.9, 460 * 0.1, 550],
    "GSHP": [640 * 0.9, 640 * 0.1, 2130]
}

def plot_combined(values, tech_name, filename):
    fig, axes = plt.subplots(1, 2, figsize=(11, 5))

    # --- Kreisdiagramm ---
    wedges, _, _ = axes[0].pie(
        values,
        autopct="%1.0f%%",
        startangle=90,
        colors=colors,
        textprops={"fontsize": 18, "weight": "bold"}
    )
    axes[0].set_title(f"{tech_name}: CAPEX-Anteile", fontsize=14, weight="bold")
    axes[0].axis("equal")

    # --- Balkendiagramm ---
    bars = axes[1].bar(labels, values, color=colors)
    axes[1].set_title(f"{tech_name}: Absolute Kosten", fontsize=14, weight="bold")
    axes[1].set_ylabel("Kosten [€]")
    axes[1].tick_params(axis="x", rotation=15)

    # Werte über Balken schreiben
    for bar in bars:
        height = bar.get_height()
        axes[1].text(
            bar.get_x() + bar.get_width() / 2,
            height + max(values) * 0.002,
            f"{height:.0f} €",
            ha="center",
            va="bottom",
            fontsize=12,
            weight="bold"
        )

    # gemeinsame Legende
    fig.legend(
        wedges,
        labels,
        loc="lower center",
        ncol=3,
        fontsize=11
    )

    plt.tight_layout(rect=[0, 0.08, 1, 1])
    plt.savefig(filename, dpi=300, bbox_inches="tight")
    plt.show()

# Für jede Technologie eine eigene Figur
for tech, values in data.items():
    plot_combined(values, tech, f"{tech}_combined.png")