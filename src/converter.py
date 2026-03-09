from oemof import solph


# ============================================================
# Hilfsfunktion
# ============================================================

def annuity_factor(i: float = 0.02, n: int = 20) -> float:
    """
    Berechnet den Annuitätsfaktor.

    Parameters
    ----------
    i : float
        Kalkulationszins [-]
    n : int
        Nutzungsdauer [a]

    Returns
    -------
    float
        Annuitätsfaktor [-]
    """
    return (i * (1 + i) ** n) / ((1 + i) ** n - 1)


def add_heat_pump(
    es,
    label: str,
    buses: dict,
    source_bus_key: str,
    cop,
    capex_specific: float,
    interest: float = 0.02,
    lifetime: int = 20,
):
    """
    Fügt eine generische elektrisch angetriebene Wärmepumpe hinzu.

    Die Wärmepumpe besitzt:
    - einen elektrischen Eingang aus dem Strombus
    - einen quellseitigen Eingang aus dem Quellbus
    - einen thermischen Ausgang zum Wärmebus

    Parameters
    ----------
    es :
        oemof EnergySystem
    label : str
        Komponentenname
    buses : dict
        Dictionary mit allen Bus-Objekten
    source_bus_key : str
        Schlüssel des Quellenbusses im buses-Dictionary,
        z. B. 'ambient_heat', 'ground_heat', 'water_heat'
    cop :
        Konstanter COP oder zeitvariable COP-Serie
    capex_specific : float
        Spezifische Investitionskosten [€/kW]
    interest : float
        Kalkulationszins [-]
    lifetime : int
        Lebensdauer [a]
    """
    af = annuity_factor(interest, lifetime)

    b_el = buses["electricity"]
    b_heat = buses["heat"]
    b_source = buses[source_bus_key]

    hp = solph.components.Converter(
        label=label,
        inputs={
            b_el: solph.flows.Flow(),
            b_source: solph.flows.Flow(),
        },
        outputs={
            b_heat: solph.flows.Flow(
                nominal_capacity=solph.Investment(
                    ep_costs=capex_specific * af,
                    
                    
                )
            )
        },
        conversion_factors={
            b_el: 1 / cop,
            b_source: (cop - 1) / cop,
        },
    )

    es.add(hp)


# ============================================================
# Wärmepumpen
# ============================================================

def add_luft_heat_pump(es, buses: dict, df):
    """
    Luft-Wasser-Wärmepumpe (ASHP) mit zeitvariablem COP.
    """
    add_heat_pump(
        es=es,
        label="ashp",
        buses=buses,
        source_bus_key="ambient_heat",
        cop=df["COP"],
        capex_specific=1550,
        interest=0.02,
        lifetime=20,
    )


def add_gshp_heat_pump(es, buses: dict, df):
    """
    Sole-Wasser-Wärmepumpe (GSHP) mit zeitvariablem COP.
    """
    add_heat_pump(
        es=es,
        label="gshp",
        buses=buses,
        source_bus_key="ground_heat",
        cop=3.5,
        capex_specific=2770,
        interest=0.02,
        lifetime=20,
    )


def add_wasser_heat_pump(es, buses: dict, df):
    """
    Wasser-Wasser-Wärmepumpe (WSHP bzw. SA-WSHP) mit zeitvariablem COP.

    Hinweis:
    Hier werden die Investitionskosten der Wärmepumpe und der
    solarthermischen Zusatzkomponente pauschal zusammengefasst.
    """

    capex_total = 1394

    add_heat_pump(
        es=es,
        label="wshp",
        buses=buses,
        source_bus_key="water_heat",
        cop=df["cop_wshp"],
        capex_specific=capex_total,
        interest=0.02,
        lifetime=20,
    )


def add_sol_heat_pump(es, buses: dict, cop: float = 3.5):
    """
    Solarunterstützte Wärmepumpe mit konstantem COP.
    """
    add_heat_pump(
        es=es,
        label="solar_hp",
        buses=buses,
        source_bus_key="water_heat",
        cop=cop,
        capex_specific=2770,
        interest=0.02,
        lifetime=20,
    )


# ============================================================
# Gasheizkessel
# ============================================================

def add_gas_boiler(es, buses: dict, efficiency: float = 0.90):
    """
    Fügt einen Gasheizkessel als Converter hinzu.

    Parameters
    ----------
    es :
        oemof EnergySystem
    buses : dict
        Dictionary mit allen Bus-Objekten
    efficiency : float
        Wirkungsgrad des Heizkessels [-]
    """
    b_gas = buses["gas"]
    b_heat = buses["heat"]

    gas_boiler = solph.components.Converter(
        label="gas_boiler",
        inputs={
            b_gas: solph.flows.Flow()
        },
        outputs={
            b_heat: solph.flows.Flow()
        },
        conversion_factors={
            b_heat: efficiency
        },
    )

    es.add(gas_boiler)
