from oemof import solph

from .buses import create_buses, add_buses_to_system

from .source import (
    add_pv_source,
    add_grid_source,
    add_gas_source,
    add_ambient_heat_source,
    add_ground_source,
    add_water_source,
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


def add_ashp_system(es, buses, df):
    add_ambient_heat_source(es, buses)
    add_luft_heat_pump(es, buses, df)
    add_gas_boiler(es, buses)


def add_gshp_system(es, buses, df):
    add_ground_source(es, buses)
    add_gshp_heat_pump(es, buses, df)
    add_gas_boiler(es, buses)


def add_sawshp_system(es, buses, df):
    add_water_source(es, buses)
    add_wasser_heat_pump(es, buses, df)
    add_gas_boiler(es, buses)


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
