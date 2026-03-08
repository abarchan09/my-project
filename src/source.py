from oemof import solph


# ============================================================
# Stromquellen
# ============================================================

def add_pv_source(es, buses: dict, df, pv_col: str = "PV_kw"):
    """
    Fügt eine PV-Anlage als exogene Stromquelle hinzu.

    Die PV-Erzeugung wird als festes Einspeiseprofil modelliert.
    Dabei wird die maximale Leistung als nominal_capacity gesetzt
    und der zeitliche Verlauf als normiertes fix-Profil abgebildet.

    Parameters
    ----------
    es :
        oemof EnergySystem
    buses : dict
        Dictionary mit allen Bus-Objekten
    df : pandas.DataFrame
        Eingabedaten mit PV-Zeitreihe
    pv_col : str
        Spaltenname der PV-Leistung [kW]
    """
    b_el = buses["electricity"]
    pv_max = df[pv_col].max()

    if pv_max <= 0:
        raise ValueError(f"Die PV-Zeitreihe '{pv_col}' enthält keine positiven Werte.")

    pv = solph.components.Source(
        label="pv_source",
        outputs={
            b_el: solph.flows.Flow(
                nominal_capacity=pv_max,
                fix=df[pv_col] / pv_max,
            )
        },
    )

    es.add(pv)


def add_grid_source(es, buses: dict, df, price_col: str = "el_price_eur_kwh"):
    """
    Fügt das öffentliche Stromnetz als unbeschränkte Stromquelle hinzu.

    Die Strombezugskosten werden über zeitvariable variable_costs abgebildet.

    Parameters
    ----------
    es :
        oemof EnergySystem
    buses : dict
        Dictionary mit allen Bus-Objekten
    df : pandas.DataFrame
        Eingabedaten mit Strompreisen
    price_col : str
        Spaltenname des Strompreises [€/kWh]
    """
    b_el = buses["electricity"]

    grid = solph.components.Source(
        label="electricity_grid",
        outputs={
            b_el: solph.flows.Flow(
                variable_costs=df[price_col]
            )
        },
    )

    es.add(grid)


# ============================================================
# Brennstoffquelle
# ============================================================

def add_gas_source(es, buses: dict, df, price_col: str = "gas_price"):
    """
    Fügt das Gasnetz als unbeschränkte Brennstoffquelle hinzu.

    Die Gaskosten werden über zeitvariable variable_costs berücksichtigt.

    Parameters
    ----------
    es :
        oemof EnergySystem
    buses : dict
        Dictionary mit allen Bus-Objekten
    df : pandas.DataFrame
        Eingabedaten mit Gaspreisen
    price_col : str
        Spaltenname des Gaspreises [€/kWh]
    """
    b_gas = buses["gas"]

    gas = solph.components.Source(
        label="gas_grid",
        outputs={
            b_gas: solph.flows.Flow(
                variable_costs=df[price_col]
            )
        },
    )

    es.add(gas)


# ============================================================
# Umweltwärmequellen
# ============================================================

def add_ambient_heat_source(es, buses: dict):
    """
    Fügt eine allgemeine Umweltwärmequelle hinzu.

    Diese Quelle repräsentiert frei verfügbare Umweltenergie
    für eine Luft-Wasser-Wärmepumpe.

    Parameters
    ----------
    es :
        oemof EnergySystem
    buses : dict
        Dictionary mit allen Bus-Objekten
    """
    b_ambient = buses["ambient_heat"]

    ambient_source = solph.components.Source(
        label="ambient_heat_source",
        outputs={
            b_ambient: solph.flows.Flow()
        },
    )

    es.add(ambient_source)


def add_ground_source(es, buses: dict):
    """
    Fügt eine Erdreichquelle für eine Sole-Wasser-Wärmepumpe hinzu.

    Parameters
    ----------
    es :
        oemof EnergySystem
    buses : dict
        Dictionary mit allen Bus-Objekten
    """
    b_ground = buses["ground_heat"]

    ground_source = solph.components.Source(
        label="ground_heat_source",
        outputs={
            b_ground: solph.flows.Flow()
        },
    )

    es.add(ground_source)


def add_water_source(es, buses: dict, variable_costs: float = 0):
    """
    Fügt eine Wasserquelle als Niedertemperaturwärmequelle hinzu.

    Diese Quelle repräsentiert z. B. Grundwasser, Flusswasser oder
    solarthermisch vorgewärmtes Wasser als Quelle der Wärmepumpe.

    Parameters
    ----------
    es :
        oemof EnergySystem
    buses : dict
        Dictionary mit allen Bus-Objekten
    variable_costs : float
        Spezifische variable Kosten der Quelle [€/kWh]
    """
    b_water = buses["water_heat"]

    water_source = solph.components.Source(
        label="water_heat_source",
        outputs={
            b_water: solph.flows.Flow(
                variable_costs=variable_costs
            )
        },
    )

    es.add(water_source)