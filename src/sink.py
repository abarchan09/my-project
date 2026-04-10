from oemof import solph


# ============================================================
# Wärmenachfrage
# ============================================================

def add_heat_demand(es, buses: dict, df, demand_col: str = "heat_demand_kw"):
    """
    Fügt die Wärmenachfrage als feste Last hinzu.

    Die Wärmelast wird als normiertes fix-Profil modelliert.
    Die maximale Last dient als nominal_capacity.

    Parameters
    ----------
    es :
        oemof EnergySystem
    buses : dict
        Dictionary mit allen Bus-Objekten
    df : pandas.DataFrame
        Eingabedaten mit Wärmelast-Zeitreihe
    demand_col : str
        Spaltenname der Wärmelast [kW]
    """
    b_heat = buses["heat"]
    demand_max = df[demand_col].max()

    if demand_max <= 0:
        raise ValueError(
            f"Die Wärmelast-Zeitreihe '{demand_col}' enthält keine positiven Werte."
        )

    demand = solph.components.Sink(
        label="heat_demand",
        inputs={
            b_heat: solph.flows.Flow(
                nominal_capacity=demand_max,
                fix=df[demand_col] / demand_max,
            )
        },
    )

    es.add(demand)


# ============================================================
# Stromexport
# ============================================================

def add_grid_export_sink(es, buses: dict, df, price_col: str = "el_price_eur_kwh"):
    """
    Fügt eine Einspeisemöglichkeit ins Stromnetz hinzu.

    Der Export wird als Sink mit negativen variablen Kosten modelliert,
    sodass Einspeiseerlöse in die Zielfunktion eingehen.

    Parameters
    ----------
    es :
        oemof EnergySystem
    buses : dict
        Dictionary mit allen Bus-Objekten
    df : pandas.DataFrame
        Eingabedaten mit Einspeisevergütung bzw. Strompreis
    price_col : str
        Spaltenname der Einspeisevergütung [€/kWh]
    """
    b_el = buses["electricity"]

    export = solph.components.Sink(
        label="grid_export",
        inputs={
            b_el: solph.flows.Flow(
                variable_costs=-df[price_col]
            )
        },
    )

    es.add(export)


# ============================================================
# Technische Überschusswärmesenke
# ============================================================

def add_heat_dump_sink(es, buses: dict, dump_costs: float = 1000):
    """
    Fügt eine technische Überschusswärmesenke hinzu.

    Diese Senke dient dazu, das Optimierungsproblem auch dann lösbar
    zu halten, wenn zeitweise mehr Wärme erzeugt als nachgefragt wird.
    Hohe variable Kosten verhindern eine reguläre Nutzung.

    Parameters
    ----------
    es :
        oemof EnergySystem
    buses : dict
        Dictionary mit allen Bus-Objekten
    dump_costs : float
        Strafkosten der Wärmeabfuhr [€/kWh]
    """
    b_heat = buses["heat"]

    heat_dump = solph.components.Sink(
        label="heat_dump",
        inputs={
            b_heat: solph.flows.Flow(
                variable_costs=dump_costs
            )
        },
    )

    es.add(heat_dump)