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
    if i == 0:
        return 1 / n
    return (i * (1 + i) ** n) / ((1 + i) ** n - 1)


def add_heat_pump(
    es,
    label: str,
    buses: dict,
    cop,
    capex_specific: float,
    source_bus_key: str = "environmental_heat",
    interest: float = 0.02,
    lifetime: int = 20,
):
    """
    Fügt eine generische elektrisch angetriebene Wärmepumpe hinzu.

    Die Wärmepumpe besitzt:
    - einen elektrischen Eingang aus dem Strombus,
    - einen quellseitigen Eingang aus dem Quellbus,
    - einen thermischen Ausgang zum Wärmebus.

    Die Investition wird auf die thermische Ausgangsleistung bezogen.

    Parameters
    ----------
    es :
        oemof EnergySystem
    label : str
        Komponentenname
    buses : dict
        Dictionary mit allen Bus-Objekten
    cop :
        Konstanter COP oder zeitvariable COP-Serie
    capex_specific : float
        Spezifische Investitionskosten [€/kW]
    source_bus_key : str
        Schlüssel des Quellbusses im buses-Dictionary
    interest : float
        Kalkulationszins [-]
    lifetime : int
        Lebensdauer [a]
    """
    if hasattr(cop, "min"):
        if cop.min() <= 1:
            raise ValueError(f"COP von '{label}' muss für alle Zeitpunkte > 1 sein.")
    else:
        if cop <= 1:
            raise ValueError(f"COP von '{label}' muss > 1 sein.")

    af = annuity_factor(interest, lifetime)
# Input
    b_el = buses["electricity"]
    b_env_heat = buses["environmental_heat"]
#output
    heat = buses["heat"]

    hp = solph.components.Converter(
        label=label,
        inputs={
            b_el: solph.flows.Flow(),
            b_env_heat: solph.flows.Flow(),
        },
        outputs={
             heat: solph.flows.Flow(
                nominal_capacity=solph.Investment(
                    ep_costs=capex_specific * af,
                    maximum=100
                    
                )
            )
        },
        conversion_factors={
            b_el: 1 / cop,
            b_env_heat: (cop - 1) / cop,
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
        cop=df["COP"],
        capex_specific=1550,
        source_bus_key="environmental_heat",
        interest=0.02,
        lifetime=20,
    )


def add_gshp_heat_pump(es, buses: dict, df=None):
    """
    Sole-Wasser-Wärmepumpe (GSHP) mit konstantem COP.
    """
    add_heat_pump(
        es=es,
        label="gshp",
        buses=buses,
        cop=3.5,
        capex_specific=2770,
        source_bus_key="environmental_heat",
        interest=0.02,
        lifetime=20,
    )


def add_wasser_heat_pump(es, buses: dict, df):
    """
    Wasser-Wasser-Wärmepumpe (WSHP) mit zeitvariablem COP.

    Hinweis:
    Die angesetzten spezifischen Investitionskosten beziehen sich
    auf die thermische Leistung der Gesamtanlage.
    """
    add_heat_pump(
        es=es,
        label="wshp",
        buses=buses,
        cop=df["cop_s_3"],
        capex_specific=1010,
        source_bus_key="environmental_heat",
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

# ============================================================
# zischen Konverter sammlt zwei Input und raus output
# ============================================================
def add_vor_convertre(es, buses: dict):
    #  input Busse
    b_solar_heat = buses["solar_heat"]
    b_storage = buses["storage_heat"]             
    
    #output  
    b_water = buses["water"] 

    storage = solph.components.Converter(
        label="vor_speicher",
        
        inputs={
            b_solar_heat: solph.flows.Flow(),
            b_storage: solph.flows.Flow()
        },
        outputs={
            b_water: solph.flows.Flow(
                

            ),
        },
      
    )

    es.add(storage)
