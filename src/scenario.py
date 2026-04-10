from oemof import solph

from .buses import create_buses, add_buses_to_system

from .source import (
    add_pv_source,
    add_grid_source,
    add_gas_source,
    add_environmental_heat_source,
    add_solar_thermal_source,
    add_storage_heat_source

)

from .sink import (
    add_heat_demand,
    add_grid_export_sink,
    add_heat_dump_sink,
)

from .converter import (
    add_luft_heat_pump,
    add_gshp_heat_pump,
    add_wasser_heat_pump,
    add_gas_boiler,
    
   
)
from .storage import(
    add_puffer_speicher,
)

def build_base_system(df):
    es = solph.EnergySystem(timeindex=df.index)
    buses = create_buses()
    add_buses_to_system(es, buses)

    add_pv_source(es, buses, df)
    add_grid_source(es, buses, df)
    add_gas_source(es, buses, df)

    add_heat_demand(es, buses, df)
    add_grid_export_sink(es, buses, df)
    add_heat_dump_sink(es, buses)

    return es, buses

#-----------SZENARIO 1--------------#
def add_ashp_system(es, buses, df):
    """
    Szenario S1: Luft-Wasser-Wärmepumpe (ASHP)

    Systemstruktur:
    - Umweltwärme (Luft) → environmental_heat
    - Strom → Wärmepumpe
    - Wärmepumpe → heat
    - Gasheizkessel → Spitzenlast

    Parameters
    ----------
    es :
        oemof EnergySystem
    buses : dict
        Bus-Dictionary
    df : pandas.DataFrame
        Zeitreihen (COP etc.)
    """

    # Umweltwärmequelle (Luft)
    add_environmental_heat_source(es, buses)

    # Wärmepumpe (ASHP)
    add_luft_heat_pump(es, buses, df)

    # Spitzenlastkessel
    add_gas_boiler(es, buses)

#-----------SZENARIO 2--------------#
def add_gshp_system(es, buses, df):
    """
    Szenario S2: Sole-Wasser-Wärmepumpe (GSHP)

    Systemstruktur:
    - Erdreich / Sole → environmental_heat
    - Strom → Wärmepumpe
    - Wärmepumpe → heat
    - Gasheizkessel → Spitzenlast
    """
    add_environmental_heat_source(es, buses)
    add_gshp_heat_pump(es, buses, df)
    add_gas_boiler(es, buses)

#-----------SZENARIO 3--------------#
def add_sawshp_system(es, buses, df):
    """
    Szenario S3: Solar-unterstützte Wasser-Wasser-Wärmepumpe (SA-WSHP)

    Systemstruktur:
    - Umweltwärme / Wasserquelle → environmental_heat
    - Solarthermie → solar_heat
    - Pufferspeicher: solar_heat → environmental_heat
    - Strom → Wärmepumpe
    - Wärmepumpe → heat
    - Gasheizkessel → Spitzenlast
    """

    # Grundlegende Quellwärme
    #add_storage_heat_source(es, buses)

    # Solarthermische Zusatzquelle
    add_solar_thermal_source(es, buses, df)

    # Speicher für solarthermische Wärme
    add_puffer_speicher(es, buses)

    # Wärmepumpe
    add_wasser_heat_pump(es, buses, df)

    # Spitzenlastkessel
    add_gas_boiler(es, buses)
   

#------------------------------------------------------------#
#        Bauen der Szenario nach der Namen der Technologien  #
def build_scenario(df, scenario_name: str):
    es, buses = build_base_system(df)
    name = scenario_name.upper()

    if name == "ASHP":
        add_ashp_system(es, buses, df)
    elif name == "GSHP":
        add_gshp_system(es, buses, df)
    elif name in ["SA-WSHP", "SA_WSHP", "WSHP"]:
        add_sawshp_system(es, buses, df)
    else:
        raise ValueError(
            f"Unbekanntes Szenario: {scenario_name}. "
            f"Erlaubt sind: ASHP, GSHP, SA-WSHP"
        )

    return es, buses
