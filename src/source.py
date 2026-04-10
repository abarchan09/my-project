from oemof import solph


# ============================================================
# Quellen des Energiesystems
# ============================================================
# In diesem Modul werden die exogenen Energiequellen des
# Energiesystems definiert. Dazu zählen:
# - Photovoltaik
# - öffentliches Stromnetz
# - Gasnetz
# - Umweltwärme
# - Solarthermie
#
# Die Quellen werden in oemof.solph als Source-Komponenten
# modelliert und an die jeweiligen Busse gekoppelt.
# ============================================================


def add_pv_source(es, buses: dict, df, pv_col: str = "PV_kw"):
    """
    Fügt eine Photovoltaikanlage als exogene Stromquelle hinzu.

    Die PV-Erzeugung wird als festes Einspeiseprofil modelliert.
    Dabei wird die maximale Leistung als Nennleistung
    (nominal_capacity) gesetzt und der zeitliche Verlauf
    als normiertes fix-Profil abgebildet.

    Parameters
    ----------
    es :
        oemof EnergySystem
    buses : dict
        Dictionary mit den Bus-Objekten
    df : pandas.DataFrame
        Eingabedaten mit PV-Zeitreihe
    pv_col : str
        Spaltenname der PV-Leistung [kW]
    """
    b_el = buses["electricity"]
    pv_max = df[pv_col].max()

    if pv_max <= 0:
        raise ValueError(
            f"Die PV-Zeitreihe '{pv_col}' enthält keine positiven Werte."
        )

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

    Die Strombezugskosten werden über zeitvariable variable_costs
    abgebildet.

    Parameters
    ----------
    es :
        oemof EnergySystem
    buses : dict
        Dictionary mit den Bus-Objekten
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


def add_gas_source(es, buses: dict, df, price_col: str = "gas_price"):
    """
    Fügt das Gasnetz als unbeschränkte Brennstoffquelle hinzu.

    Die Gaskosten werden über variable_costs berücksichtigt.

    Parameters
    ----------
    es :
        oemof EnergySystem
    buses : dict
        Dictionary mit den Bus-Objekten
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


def add_environmental_heat_source(es, buses: dict):
    """
    Fügt eine allgemeine Umweltwärmequelle hinzu.

    Diese Quelle repräsentiert die frei verfügbare Umweltenergie
    als Niedertemperatur-Wärmequelle für Wärmepumpensysteme,
    z. B. Luft, Erdreich oder Grundwasser.

    Parameters
    ----------
    es :
        oemof EnergySystem
    buses : dict
        Dictionary mit den Bus-Objekten
    """
    b_env_heat = buses["environmental_heat"]

    env_heat = solph.components.Source(
        label="environmental_heat_source",
        outputs={
            b_env_heat: solph.flows.Flow()
            
        },
    )

    es.add(env_heat)


def add_solar_thermal_source(es, buses: dict, df, profile_col: str = "solar_profil"):
    """
    Fügt eine solarthermische Quelle als exogene Wärmequelle hinzu.

    Die solarthermische Einspeisung wird über ein festes
    Erzeugungsprofil modelliert. Das Profil wird auf die maximale
    Leistung normiert und mit einer Nennleistung skaliert.

    Parameters
    ----------
    es :
        oemof EnergySystem
    buses : dict
        Dictionary mit den Bus-Objekten
    df : pandas.DataFrame
        Eingabedaten mit solarthermischem Leistungsprofil
    profile_col : str
        Spaltenname des solarthermischen Profils [kW]
    """
    b_solar_heat = buses["solar_heat"]
    solar_max = 350.0   #kW
    nutzungsgrad= 0.37
    capex_total= 540     #€/kWh
    annuity_factor = 0.0612
    ep_costs= (capex_total * annuity_factor) / solar_max
    if solar_max <= 0:
        raise ValueError(
            f"Die Solarthermie-Zeitreihe '{profile_col}' enthält keine positiven Werte."
        )

    solar = solph.components.Source(
        label="solar_thermal_source",
        outputs={
            b_solar_heat: solph.flows.Flow(
                nominal_capacity=solph.Investment(
                    ep_costs=ep_costs
                ) ,
                fix=df[profile_col]
                
            )
        },
    )

    es.add(solar)


def add_storage_heat_source(es, buses: dict):
    """
    Fügt eine allgemeine Umweltwärmequelle hinzu.

    Diese Quelle repräsentiert die frei verfügbare Umweltenergie
    als Niedertemperatur-Wärmequelle für Wärmepumpensysteme,
    z. B. Luft, Erdreich oder Grundwasser.

    Parameters
    ----------
    es :
        oemof EnergySystem
    buses : dict
        Dictionary mit den Bus-Objekten
    """
    b_storage = buses["storage_heat"]

    st_heat = solph.components.Source(
        label="environmental_heat_source",
        outputs={
            b_storage: solph.flows.Flow()
        },
    )

    es.add(st_heat)   