import matplotlib.pyplot as plt

def plot_pv_grid_heatdemand(output_data, rolling=True, window=168):
    """
    data: dict aus extract_result_series(results)
    """

    heat_demand = output_data["heat_demand"]
    hp_heat     = output_data["hp_heat"]
    boiler_heat = output_data["boiler_heat"]

    if rolling:
        heat_demand = heat_demand.rolling(window).mean()
        hp_heat     = hp_heat.rolling(window).mean()
        boiler_heat = boiler_heat.rolling(window).mean()

    fig, ax = plt.subplots(figsize=(14, 6))
    ax.stackplot(
        heat_demand.index,
        hp_heat.values,
        boiler_heat.values,
        labels=["Wärmepumpe", "Gasboiler"],
        alpha=0.8,
    )
    ax.plot(heat_demand.index, heat_demand.values, label="Wärmebedarf (Gesamt)", linewidth=2.5)

    ax.set_ylabel("Wärmeleistung (kW)")
    ax.set_xlabel("Zeit")
    ax.grid(alpha=0.3)
    ax.legend(loc="upper right")
    ax.set_title("Deckungsanteile am Wärmebedarf (HP + Gasboiler)")
    plt.tight_layout()
    plt.show()