import matplotlib.pyplot as plt
import pandas as pd


def _safe_zero_series(reference_index):
    """Erzeugt eine Null-Zeitreihe mit passendem Index."""
    return pd.Series(0.0, index=reference_index)


def _get_series(output_data, key, reference_index):
    """Liest Zeitreihe aus output_data, sonst Null-Zeitreihe."""
    s = output_data.get(key)
    if s is None:
        return _safe_zero_series(reference_index)
    return s.fillna(0)


def plot_heat_supply(output_data, rolling=True, window=168):
    """
    Plot der Deckung des Wärmebedarfs durch Wärmepumpe(n) und Gasboiler.

    Parameters
    ----------
    output_data : dict
        Dictionary aus extract_result_series(results)
    rolling : bool, optional
        Ob Zeitreihen geglättet werden sollen
    window : int, optional
        Fenstergröße für rolling mean, Standard: 168 h = 1 Woche
    """

    heat_demand = output_data.get("heat_demand")
    if heat_demand is None:
        raise ValueError("output_data enthält keine Zeitreihe 'heat_demand'.")

    heat_demand = heat_demand.fillna(0)

    ashp_heat = _get_series(output_data, "ashp_heat", heat_demand.index)
    gshp_heat = _get_series(output_data, "gshp_heat", heat_demand.index)
    wshp_heat = _get_series(output_data, "wshp_heat", heat_demand.index)
    gas_boiler_heat = _get_series(output_data, "gas_boiler_heat", heat_demand.index)

    # gesamte Wärmepumpenwärme
    hp_heat_total = ashp_heat + gshp_heat + wshp_heat

    # Glättung
    if rolling:
        heat_demand = heat_demand.rolling(window, min_periods=1).mean()
        ashp_heat = ashp_heat.rolling(window, min_periods=1).mean()
        gshp_heat = gshp_heat.rolling(window, min_periods=1).mean()
        wshp_heat = wshp_heat.rolling(window, min_periods=1).mean()
        gas_boiler_heat = gas_boiler_heat.rolling(window, min_periods=1).mean()
        hp_heat_total = hp_heat_total.rolling(window, min_periods=1).mean()

    fig, ax = plt.subplots(figsize=(14, 6))

    # nur vorhandene Reihen plotten
    stack_series = []
    stack_labels = []

    if ashp_heat.sum() > 0:
        stack_series.append(ashp_heat.values)
        stack_labels.append("ASHP")

    if gshp_heat.sum() > 0:
        stack_series.append(gshp_heat.values)
        stack_labels.append("GSHP")

    if wshp_heat.sum() > 0:
        stack_series.append(wshp_heat.values)
        stack_labels.append("WSHP")

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

    ax.plot(
        heat_demand.index,
        heat_demand.values,
        label="Wärmebedarf (Gesamt)",
        linewidth=2.5,
        color="black",
    )

    ax.set_ylabel("Wärmeleistung (kW)")
    ax.set_xlabel("Zeit")
    ax.set_title("Deckung des Wärmebedarfs")
    ax.grid(alpha=0.3)
    ax.legend(loc="upper right")

    plt.tight_layout()
    plt.show()


def plot_heat_supply_simple(output_data, rolling=True, window=168):
    """
    Einfacher Plot: gesamte Wärmepumpenwärme vs. Gasboiler.
    Gut für kompakte Darstellung in der Bachelorarbeit.
    """

    heat_demand = output_data.get("heat_demand")
    if heat_demand is None:
        raise ValueError("output_data enthält keine Zeitreihe 'heat_demand'.")

    heat_demand = heat_demand.fillna(0)

    ashp_heat = _get_series(output_data, "ashp_heat", heat_demand.index)
    gshp_heat = _get_series(output_data, "gshp_heat", heat_demand.index)
    wshp_heat = _get_series(output_data, "wshp_heat", heat_demand.index)
    gas_boiler_heat = _get_series(output_data, "gas_boiler_heat", heat_demand.index)

    hp_heat_total = ashp_heat + gshp_heat + wshp_heat

    if rolling:
        heat_demand = heat_demand.rolling(window, min_periods=1).mean()
        hp_heat_total = hp_heat_total.rolling(window, min_periods=1).mean()
        gas_boiler_heat = gas_boiler_heat.rolling(window, min_periods=1).mean()

    fig, ax = plt.subplots(figsize=(14, 6))

    ax.stackplot(
        heat_demand.index,
        hp_heat_total.values,
        gas_boiler_heat.values,
        labels=["Wärmepumpe", "Gasboiler"],
        alpha=0.8,
    )

    ax.plot(
        heat_demand.index,
        heat_demand.values,
        label="Wärmebedarf (Gesamt)",
        linewidth=2.5,
        color="black",
    )

    ax.set_ylabel("Wärmeleistung (kW)")
    ax.set_xlabel("Zeit")
    ax.set_title("Deckung des Wärmebedarfs durch Wärmepumpe und Gasboiler")
    ax.grid(alpha=0.3)
    ax.legend(loc="upper right")

    plt.tight_layout()
    plt.show()