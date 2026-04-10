import pandas as pd
from oemof.solph import views


# ============================================================
# Hilfsfunktionen
# ============================================================

def get_invest_value(node_view, key: str = "invest"):
    """
    Liest den Investitionswert aus den scalars eines Knotens aus.
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


def get_sequence_or_none(node_sequences, from_label: str, to_label: str):
    """
    Liest eine Sequenz aus einem views.node(...)-Objekt robust aus.
    """
    return node_sequences.get(((from_label, to_label), "flow"))


# ============================================================
# Zeitreihen extrahieren
# ============================================================

def extract_result_series(results):
    """
    Extrahiert zentrale Zeitreihen aus dem oemof-Ergebnisobjekt.
    """
    data = {}

    # --------------------------------------------------------
    # Strombus
    # --------------------------------------------------------
    try:
        el_seq = views.node(results, "electricity")["sequences"]
        data["grid_import_el"] = get_sequence_or_none(el_seq, "electricity_grid", "electricity")
        data["pv_el"] = get_sequence_or_none(el_seq, "pv_source", "electricity")
        data["grid_export_el"] = get_sequence_or_none(el_seq, "electricity", "grid_export")
    except Exception:
        data["grid_import_el"] = None
        data["pv_el"] = None
        data["grid_export_el"] = None

    # --------------------------------------------------------
    # Gasbus
    # --------------------------------------------------------
    try:
        gas_seq = views.node(results, "gas")["sequences"]
        data["gas_import"] = get_sequence_or_none(gas_seq, "gas_grid", "gas")
        data["gas_to_boiler"] = get_sequence_or_none(gas_seq, "gas", "gas_boiler")
    except Exception:
        data["gas_import"] = None
        data["gas_to_boiler"] = None

    # --------------------------------------------------------
    # Wärmebus
    # --------------------------------------------------------
    try:
        heat_seq = views.node(results, "heat")["sequences"]
        data["heat_demand"] = get_sequence_or_none(heat_seq, "heat", "heat_demand")
        data["heat_dump"] = get_sequence_or_none(heat_seq, "heat", "heat_dump")
        data["gas_boiler_heat"] = get_sequence_or_none(heat_seq, "gas_boiler", "heat")
        data["ashp_heat"] = get_sequence_or_none(heat_seq, "ashp", "heat")
        data["gshp_heat"] = get_sequence_or_none(heat_seq, "gshp", "heat")
        data["wshp_heat"] = get_sequence_or_none(heat_seq, "wshp", "heat")
    except Exception:
        data["heat_demand"] = None
        data["heat_dump"] = None
        data["gas_boiler_heat"] = None
        data["ashp_heat"] = None
        data["gshp_heat"] = None
        data["wshp_heat"] = None

    # --------------------------------------------------------
    # Solarthermie-Bus
    # --------------------------------------------------------
    try:
        solar_seq = views.node(results, "solar_heat")["sequences"]
        data["solar_thermal_generation"] = get_sequence_or_none(
            solar_seq, "solar_thermal_source", "solar_heat"
        )
        data["solar_to_preconverter"] = get_sequence_or_none(
            solar_seq, "solar_heat", "vor_speicher"
        )
    except Exception:
        data["solar_thermal_generation"] = None
        data["solar_to_preconverter"] = None

    # --------------------------------------------------------
    # storage_heat-Bus
    # --------------------------------------------------------
    try:
        sh_seq = views.node(results, "storage_heat")["sequences"]
        data["storage_heat_source_generation"] = get_sequence_or_none(
            sh_seq, "environmental_heat_source", "storage_heat"
        )
        data["storage_heat_to_preconverter"] = get_sequence_or_none(
            sh_seq, "storage_heat", "vor_speicher"
        )
    except Exception:
        data["storage_heat_source_generation"] = None
        data["storage_heat_to_preconverter"] = None

    # --------------------------------------------------------
    # water-Bus
    # --------------------------------------------------------
    try:
        water_seq = views.node(results, "water")["sequences"]
        data["preconverter_to_water"] = get_sequence_or_none(
            water_seq, "vor_speicher", "water"
        )
        data["water_to_storage"] = get_sequence_or_none(
            water_seq, "water", "pufferspeicher"
        )
    except Exception:
        data["preconverter_to_water"] = None
        data["water_to_storage"] = None

    # --------------------------------------------------------
    # Umweltwärme-Bus
    # --------------------------------------------------------
    try:
        env_seq = views.node(results, "environmental_heat")["sequences"]
        data["environmental_source_heat"] = get_sequence_or_none(
            env_seq, "environmental_heat_source", "environmental_heat"
        )
        data["storage_to_env_heat"] = get_sequence_or_none(
            env_seq, "pufferspeicher", "environmental_heat"
        )
        data["env_heat_to_ashp"] = get_sequence_or_none(
            env_seq, "environmental_heat", "ashp"
        )
        data["env_heat_to_gshp"] = get_sequence_or_none(
            env_seq, "environmental_heat", "gshp"
        )
        data["env_heat_to_wshp"] = get_sequence_or_none(
            env_seq, "environmental_heat", "wshp"
        )
    except Exception:
        data["environmental_source_heat"] = None
        data["storage_to_env_heat"] = None
        data["env_heat_to_ashp"] = None
        data["env_heat_to_gshp"] = None
        data["env_heat_to_wshp"] = None

    # --------------------------------------------------------
    # Speicher
    # --------------------------------------------------------
    try:
        storage_node = views.node(results, "pufferspeicher")
        storage_seq = storage_node["sequences"]

        data["storage_in"] = get_sequence_or_none(
            storage_seq, "water", "pufferspeicher"
        )
        data["storage_out"] = get_sequence_or_none(
            storage_seq, "pufferspeicher", "environmental_heat"
        )

        storage_content = None
        for col in storage_seq.columns:
            if "storage_content" in str(col).lower():
                storage_content = storage_seq[col]
                break
        data["storage_content"] = storage_content

    except Exception:
        data["storage_in"] = None
        data["storage_out"] = None
        data["storage_content"] = None

    return data


# ============================================================
# Investitionen extrahieren
# ============================================================

def extract_investments(results):
    """
    Extrahiert Investitionsentscheidungen relevanter Komponenten.
    """
    investments = {}

    for label in [
        "ashp",
        "gshp",
        "wshp",
        "gas_boiler",
        "pufferspeicher",
        "solar_thermal_source",
    ]:
        try:
            node_data = views.node(results, label)
            investments[label] = get_invest_value(node_data)
        except Exception:
            investments[label] = 0.0

    return investments


# ============================================================
# Kennzahlen berechnen
# ============================================================

def calculate_summary(results, scenario_name: str):
    """
    Berechnet zentrale techno-ökonomische Kennzahlen.
    """
    ts = extract_result_series(results)
    inv = extract_investments(results)

    grid_import = safe_series_sum(ts["grid_import_el"])
    pv_el = safe_series_sum(ts["pv_el"])
    grid_export = safe_series_sum(ts["grid_export_el"])
    gas_import = safe_series_sum(ts["gas_import"])
    gas_to_boiler = safe_series_sum(ts["gas_to_boiler"])

    heat_demand = safe_series_sum(ts["heat_demand"])
    heat_dump = safe_series_sum(ts["heat_dump"])

    solar_generation = safe_series_sum(ts["solar_thermal_generation"])
    solar_to_preconverter = safe_series_sum(ts["solar_to_preconverter"])

    storage_heat_source_generation = safe_series_sum(ts["storage_heat_source_generation"])
    storage_heat_to_preconverter = safe_series_sum(ts["storage_heat_to_preconverter"])

    preconverter_to_water = safe_series_sum(ts["preconverter_to_water"])
    water_to_storage = safe_series_sum(ts["water_to_storage"])

    storage_in = safe_series_sum(ts["storage_in"])
    storage_out = safe_series_sum(ts["storage_out"])

    environmental_source_heat = safe_series_sum(ts["environmental_source_heat"])
    storage_to_env_heat = safe_series_sum(ts["storage_to_env_heat"])

    hp_heat = (
        safe_series_sum(ts["ashp_heat"])
        + safe_series_sum(ts["gshp_heat"])
        + safe_series_sum(ts["wshp_heat"])
    )
    gas_boiler_heat = safe_series_sum(ts["gas_boiler_heat"])

    installed_hp_capacity = inv["ashp"] + inv["gshp"] + inv["wshp"]
    installed_gas_boiler_capacity = inv["gas_boiler"]
    installed_storage_capacity = inv["pufferspeicher"]
    installed_solar_capacity = inv["solar_thermal_source"]

    summary = {
        "scenario": scenario_name,
        "grid_import_el_kWh": grid_import,
        "pv_generation_kWh": pv_el,
        "grid_export_el_kWh": grid_export,
        "gas_import_kWh": gas_import,
        "gas_to_boiler_kWh": gas_to_boiler,
        "heat_demand_kWh": heat_demand,
        "heat_dump_kWh": heat_dump,
        "heat_from_hp_kWh": hp_heat,
        "heat_from_gas_boiler_kWh": gas_boiler_heat,
        "solar_thermal_generation_kWh": solar_generation,
        "solar_to_preconverter_kWh": solar_to_preconverter,
        "storage_heat_source_generation_kWh": storage_heat_source_generation,
        "storage_heat_to_preconverter_kWh": storage_heat_to_preconverter,
        "preconverter_to_water_kWh": preconverter_to_water,
        "water_to_storage_kWh": water_to_storage,
        "storage_charge_kWh": storage_in,
        "storage_discharge_kWh": storage_out,
        "environmental_source_heat_kWh": environmental_source_heat,
        "storage_to_environmental_heat_kWh": storage_to_env_heat,
        "installed_hp_capacity_kW": installed_hp_capacity,
        "installed_gas_boiler_capacity_kW": installed_gas_boiler_capacity,
        "installed_storage_capacity_kWh": installed_storage_capacity,
        "installed_solar_capacity_kW": installed_solar_capacity,
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