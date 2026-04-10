import matplotlib.pyplot as plt
import pandas as pd


def _safe_zero_series(reference_index):
    return pd.Series(0.0, index=reference_index)


def _get_series(output_data, key, reference_index):
    s = output_data.get(key)
    if s is None:
        return _safe_zero_series(reference_index)
    return s.fillna(0)


def plot_heat_supply_simple(
    output_data,
    rolling=True,
    window=168,
    save_path="betriebsverhalten_szenario.svg"
):
    """
    Vereinfachter Plot der Wärmebereitstellung.
    """

    heat_demand = output_data.get("heat_demand")
    if heat_demand is None:
        raise ValueError("output_data enthält keine Zeitreihe 'heat_demand'.")

    heat_demand = heat_demand.fillna(0)

    ashp_heat = _get_series(output_data, "ashp_heat", heat_demand.index)
    gshp_heat = _get_series(output_data, "gshp_heat", heat_demand.index)
    wshp_heat = _get_series(output_data, "wshp_heat", heat_demand.index)
    gas_boiler_heat = _get_series(output_data, "gas_boiler_heat", heat_demand.index)

    storage_charge = _get_series(output_data, "storage_in", heat_demand.index)
    storage_discharge = _get_series(output_data, "storage_out", heat_demand.index)

    # gesamte Wärmepumpenwärme
    hp_heat_total = ashp_heat + gshp_heat + wshp_heat

    # Debug-Ausgabe
    print("Summe ASHP:", ashp_heat.sum())
    print("Summe GSHP:", gshp_heat.sum())
    print("Summe WSHP:", wshp_heat.sum())
    print("Summe HP gesamt:", hp_heat_total.sum())
    print("Summe Gasboiler:", gas_boiler_heat.sum())

    if rolling:
        heat_demand = heat_demand.rolling(window, min_periods=1).mean()
        hp_heat_total = hp_heat_total.rolling(window, min_periods=1).mean()
        gas_boiler_heat = gas_boiler_heat.rolling(window, min_periods=1).mean()
        storage_charge = storage_charge.rolling(window, min_periods=1).mean()
        storage_discharge = storage_discharge.rolling(window, min_periods=1).mean()

    fig, ax = plt.subplots(figsize=(12, 4))

    # Stackplot nur mit Gesamt-HP + Gas
    stack_series = []
    stack_labels = []

    if hp_heat_total.sum() > 0:
        stack_series.append(hp_heat_total.values)
        stack_labels.append("Wärmepumpe")

    if gas_boiler_heat.sum() > 0:
        stack_series.append(gas_boiler_heat.values)
        stack_labels.append("Gasboiler")

    if stack_series:
        ax.stackplot(
            heat_demand.index,
            *stack_series,
            labels=stack_labels,
            alpha=0.8,
        )

    # Wärmebedarf schwarz darüber
    ax.plot(
        heat_demand.index,
        heat_demand.values,
        label="Wärmebedarf",
        linewidth=2.2,
        color="black",
    )

    # Speicher optional
    if storage_charge.sum() > 0:
        ax.plot(
            heat_demand.index,
            storage_charge.values,
            label="Speicheraufladung",
            linestyle="--",
            linewidth=1.5,
        )

    if storage_discharge.sum() > 0:
        ax.plot(
            heat_demand.index,
            storage_discharge.values,
            label="Speicherentladung",
            linestyle=":",
            linewidth=1.7,
        )

    ax.set_ylabel("Wärmeleistung in kW")
    ax.set_xlabel("Zeit")
    ax.set_title("Deckung des Wärmebedarfs durch Wärmepumpe, Gasboiler und Speicher")
    ax.grid(alpha=0.3)
    ax.legend(loc="upper right")

    plt.tight_layout()
    plt.savefig(save_path, bbox_inches="tight")
    plt.show()