import pandas as pd
from oemof.solph import views


# ============================================================
# Hilfsfunktion
# ============================================================

def get_invest_value(node_view, key: str = "invest"):
    """
    Liest den Investitionswert aus den scalars eines Knotens aus.

    Parameters
    ----------
    node_view : dict
        Ausgabe von views.node(results, "label")
    key : str
        Name des Scalar-Eintrags

    Returns
    -------
    float
        Investitionswert oder 0.0, falls nicht vorhanden
    """
    scalars = node_view.get("scalars", None)
    if scalars is None or len(scalars) == 0:
        return 0.0

    for idx, value in scalars.items():
        if key in str(idx).lower():
            return float(value)

    return 0.0


def safe_series_sum(series):
    """
    Summiert eine Zeitreihe robust auf.
    """
    if series is None:
        return 0.0
    return float(series.fillna(0).sum())


# ============================================================
# Zeitreihen extrahieren
# ============================================================

def extract_result_series(results):
    """
    Extrahiert zentrale Zeitreihen aus dem oemof-Ergebnisobjekt.

    Returns
    -------
    dict
        Dictionary mit relevanten Ergebnis-Zeitreihen
    """
    data = {}

    try:
        el_seq = views.node(results, "electricity")["sequences"]
        data["grid_import_el"] = el_seq.get((("electricity_grid", "electricity"), "flow"))
        data["pv_el"] = el_seq.get((("pv_source", "electricity"), "flow"))
        data["grid_export_el"] = el_seq.get((("electricity", "grid_export"), "flow"))
    except Exception:
        data["grid_import_el"] = None
        data["pv_el"] = None
        data["grid_export_el"] = None

    try:
        gas_seq = views.node(results, "gas")["sequences"]
        data["gas_import"] = gas_seq.get((("gas_grid", "gas"), "flow"))
    except Exception:
        data["gas_import"] = None

    try:
        heat_seq = views.node(results, "heat")["sequences"]
        data["heat_demand"] = heat_seq.get((("heat", "heat_demand"), "flow"))
        data["heat_dump"] = heat_seq.get((("heat", "heat_dump"), "flow"))
        data["gas_boiler_heat"] = heat_seq.get((("gas_boiler", "heat"), "flow"))
        data["ashp_heat"] = heat_seq.get((("ashp", "heat"), "flow"))
        data["gshp_heat"] = heat_seq.get((("gshp", "heat"), "flow"))
        data["wshp_heat"] = heat_seq.get((("wshp", "heat"), "flow"))
    except Exception:
        data["heat_demand"] = None
        data["heat_dump"] = None
        data["gas_boiler_heat"] = None
        data["ashp_heat"] = None
        data["gshp_heat"] = None
        data["wshp_heat"] = None

    return data


# ============================================================
# Investitionen extrahieren
# ============================================================

def extract_investments(results):
    """
    Extrahiert Investitionsentscheidungen relevanter Komponenten.

    Returns
    -------
    dict
        Dictionary mit Investitionswerten
    """
    investments = {}

    for label in ["ashp", "gshp", "wshp", "gas_boiler"]:
        try:
            node_data = views.node(results, label)
            investments[label] = get_invest_value(node_data)
        except Exception:
            investments[label] = 0.0

    return investments


# ============================================================
# Kennzahlen berechnen
# ============================================================

def calculate_summary(results, scenario_name: str, heat_price_unit: str = "kWh"):
    """
    Berechnet zentrale techno-ökonomische Kennzahlen.

    Parameters
    ----------
    results : dict
        oemof-Ergebnisse
    scenario_name : str
        Name des Szenarios
    heat_price_unit : str
        'kWh' oder 'MWh' für die LCOH-Ausgabe

    Returns
    -------
    pandas.DataFrame
        Zusammenfassende Kennzahlen
    """
    ts = extract_result_series(results)
    inv = extract_investments(results)

    grid_import = safe_series_sum(ts["grid_import_el"])
    pv_el = safe_series_sum(ts["pv_el"])
    grid_export = safe_series_sum(ts["grid_export_el"])
    gas_import = safe_series_sum(ts["gas_import"])
    heat_demand = safe_series_sum(ts["heat_demand"])
    heat_dump = safe_series_sum(ts["heat_dump"])

    hp_heat = (
        safe_series_sum(ts["ashp_heat"])
        + safe_series_sum(ts["gshp_heat"])
        + safe_series_sum(ts["wshp_heat"])
    )
    gas_boiler_heat = safe_series_sum(ts["gas_boiler_heat"])

    installed_hp_capacity = inv["ashp"] + inv["gshp"] + inv["wshp"]
    installed_gas_boiler_capacity = inv["gas_boiler"]

    # Achtung:
    # Hier ist "invest" zunächst nur die installierte Leistung.
    # CAPEX ergibt sich erst mit spezifischen Kosten außerhalb dieser Funktion,
    # falls du ihn separat berechnen willst.
    summary = {
        "scenario": scenario_name,
        "grid_import_el_kWh": grid_import,
        "pv_generation_kWh": pv_el,
        "grid_export_el_kWh": grid_export,
        "gas_import_kWh": gas_import,
        "heat_demand_kWh": heat_demand,
        "heat_dump_kWh": heat_dump,
        "heat_from_hp_kWh": hp_heat,
        "heat_from_gas_boiler_kWh": gas_boiler_heat,
        "installed_hp_capacity_kW": installed_hp_capacity,
        "installed_gas_boiler_capacity_kW": installed_gas_boiler_capacity,
    }

    return pd.DataFrame([summary])


# ============================================================
# CSV speichern
# ============================================================

def save_summary_to_csv(summary_df: pd.DataFrame, output_path: str):
    """
    Speichert die Zusammenfassung als CSV-Datei.
    """
    summary_df.to_csv(output_path, index=False, encoding="utf-8-sig")