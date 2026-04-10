import pandas as pd
from src.evaluate import extract_result_series, extract_investments, safe_series_sum


def annuity_factor(i: float, n: int) -> float:
    """
    Kapitalwiedergewinnungsfaktor.

    Parameters
    ----------
    i : float
        Zinssatz, z. B. 0.02 für 2 %
    n : int
        Lebensdauer in Jahren

    Returns
    -------
    float
        Annuitätsfaktor
    """
    if i == 0:
        return 1 / n
    return (i * (1 + i) ** n) / ((1 + i) ** n - 1)


def get_hp_heat(results) -> float:
    """
    Summiert die erzeugte Wärme aller Wärmepumpen.
    """
    ts = extract_result_series(results)
    return (
        safe_series_sum(ts.get("ashp_heat"))
        + safe_series_sum(ts.get("gshp_heat"))
        + safe_series_sum(ts.get("wshp_heat"))
    )


def get_hp_capacity(inv: dict) -> float:
    """
    Summiert die installierte Wärmepumpenleistung.
    """
    return (
        inv.get("ashp", 0.0)
        + inv.get("gshp", 0.0)
        + inv.get("wshp", 0.0)
    )


def calculate_capex_hp(
    results,
    scenario_name: str,
    capex_ashp_kw: float = 1550,
    capex_gshp_kw: float = 2770,
    capex_wshp_kw: float = 1010,
    capex_solar_kw: float | None = None,
    capex_storage_total_eur: float | None = None,
) -> float:
    """
    Berechnet den gesamten CAPEX des Wärmepumpensystems.

    Hinweise
    --------
    - ASHP: nur ASHP
    - GSHP: nur GSHP
    - SA-WSHP: WSHP + Solarthermie + Pufferspeicher

    Falls Solarthermie und Speicher im oemof-Modell investiv optimiert werden,
    sollte capex_solar_kw angegeben werden, damit die installierte Solarleistung
    aus den Ergebnissen verwendet wird.

    Parameters
    ----------
    results : dict
        oemof-Ergebnisse
    scenario_name : str
        Name des Szenarios
    capex_ashp_kw : float
        Spezifische CAPEX ASHP [€/kW]
    capex_gshp_kw : float
        Spezifische CAPEX GSHP [€/kW]
    capex_wshp_kw : float
        Spezifische CAPEX WSHP [€/kW]
    capex_solar_kw : float | None
        Spezifische CAPEX Solarthermie [€/kW]
    capex_storage_total_eur : float | None
        Gesamtkosten des Pufferspeichers [€], falls fester Speicher

    Returns
    -------
    float
        Gesamt-CAPEX des HP-Systems [€]
    """
    inv = extract_investments(results)

    if scenario_name == "ASHP":
        return float(inv.get("ashp", 0.0) * capex_ashp_kw)

    if scenario_name == "GSHP":
        return float(inv.get("gshp", 0.0) * capex_gshp_kw)

    if scenario_name == "SA-WSHP":
        capex_total = inv.get("wshp", 0.0) * capex_wshp_kw

        # Solarthermie nur addieren, wenn sie investiv modelliert wurde
        if capex_solar_kw is not None:
            capex_total += inv.get("solar_thermal_source", 0.0) * capex_solar_kw

        # Pufferspeicher als fixer Gesamtbetrag
        if capex_storage_total_eur is not None:
            capex_total += capex_storage_total_eur

        return float(capex_total)

    return 0.0


def calculate_opex_hp(
    results,
    electricity_price_per_kwh: float | None = None,
    electricity_price_series: pd.Series | None = None,
) -> float:
    """
    OPEX der Wärmepumpe nur aus Strombezug.

    Entweder fixer Strompreis oder Zeitreihe angeben.
    """
    ts = extract_result_series(results)

    grid_import_el = ts.get("grid_import_el")
    if grid_import_el is None:
        return 0.0

    if electricity_price_series is not None:
        aligned_price = electricity_price_series.reindex(grid_import_el.index).ffill().bfill()
        return float((grid_import_el.fillna(0) * aligned_price).sum())

    if electricity_price_per_kwh is not None:
        return float(grid_import_el.fillna(0).sum() * electricity_price_per_kwh)

    return 0.0


def calculate_opex_system(
    results,
    electricity_price_per_kwh: float | None = None,
    gas_price_per_kwh: float | None = None,
    electricity_price_series: pd.Series | None = None,
    gas_price_series: pd.Series | None = None,
) -> float:
    """
    OPEX des Gesamtsystems = Stromkosten + Gaskosten - Exporterlöse.
    """
    ts = extract_result_series(results)

    grid_import_el = ts.get("grid_import_el")
    gas_import = ts.get("gas_import")
    grid_export_el = ts.get("grid_export_el")

    opex_el = 0.0
    opex_gas = 0.0
    export_revenue = 0.0

    if grid_import_el is not None:
        if electricity_price_series is not None:
            el_price = electricity_price_series.reindex(grid_import_el.index).ffill().bfill()
            opex_el = float((grid_import_el.fillna(0) * el_price).sum())
        elif electricity_price_per_kwh is not None:
            opex_el = float(grid_import_el.fillna(0).sum() * electricity_price_per_kwh)

    if gas_import is not None:
        if gas_price_series is not None:
            gas_price = gas_price_series.reindex(gas_import.index).ffill().bfill()
            opex_gas = float((gas_import.fillna(0) * gas_price).sum())
        elif gas_price_per_kwh is not None:
            opex_gas = float(gas_import.fillna(0).sum() * gas_price_per_kwh)

    if grid_export_el is not None:
        if electricity_price_series is not None:
            export_price = electricity_price_series.reindex(grid_export_el.index).ffill().bfill()
            export_revenue = float((grid_export_el.fillna(0) * export_price).sum())
        elif electricity_price_per_kwh is not None:
            export_revenue = float(grid_export_el.fillna(0).sum() * electricity_price_per_kwh)

    return opex_el + opex_gas - export_revenue


def calculate_spf_hp(results) -> float:
    """
    SPF der Wärmepumpe:
    SPF_hp = erzeugte HP-Wärme / eingesetzter Strom
    """
    ts = extract_result_series(results)

    hp_heat = get_hp_heat(results)
    grid_import_el = safe_series_sum(ts.get("grid_import_el"))

    if grid_import_el <= 0:
        return 0.0

    return hp_heat / grid_import_el


def calculate_spf_system(results) -> float:
    """
    SPF des Gesamtsystems:
    SPF_system = gesamte Nutzwärme / (Strombezug + Gasbezug)
    """
    ts = extract_result_series(results)

    useful_heat = safe_series_sum(ts.get("heat_demand"))
    grid_import_el = safe_series_sum(ts.get("grid_import_el"))
    gas_import = safe_series_sum(ts.get("gas_import"))

    denominator = grid_import_el + gas_import
    if denominator <= 0:
        return 0.0

    return useful_heat / denominator


def calculate_lcoh_hp(
    results,
    scenario_name: str,
    capex_ashp_kw: float = 1550,
    capex_gshp_kw: float = 2770,
    capex_wshp_kw: float = 1010,
    capex_solar_kw: float | None = None,
    capex_storage_total_eur: float | None = None,
    electricity_price_per_kwh: float | None = None,
    electricity_price_series: pd.Series | None = None,
    lifetime: int = 20,
    interest_rate: float = 0.02,
) -> float:
    """
    LCOH des HP-Systems.

    Bei SA-WSHP wird das System aus WSHP + Solarthermie + Speicher
    gemeinsam betrachtet.
    """
    q_hp = get_hp_heat(results)

    if q_hp <= 0:
        return 0.0

    capex_hp = calculate_capex_hp(
        results=results,
        scenario_name=scenario_name,
        capex_ashp_kw=capex_ashp_kw,
        capex_gshp_kw=capex_gshp_kw,
        capex_wshp_kw=capex_wshp_kw,
        capex_solar_kw=capex_solar_kw,
        capex_storage_total_eur=capex_storage_total_eur,
    )

    opex_hp = calculate_opex_hp(
        results=results,
        electricity_price_per_kwh=electricity_price_per_kwh,
        electricity_price_series=electricity_price_series,
    )

    a = annuity_factor(interest_rate, lifetime)
    return (capex_hp * a + opex_hp) / q_hp


def calculate_lcoh_system(
    results,
    capex_hp_total: float,
    capex_gas_boiler_total: float = 0.0,
    electricity_price_per_kwh: float | None = None,
    gas_price_per_kwh: float | None = None,
    electricity_price_series: pd.Series | None = None,
    gas_price_series: pd.Series | None = None,
    lifetime: int = 20,
    interest_rate: float = 0.02,
) -> float:
    """
    LCOH des Gesamtsystems.

    LCOH_system = ((CAPEX_hp + CAPEX_boiler) * a + OPEX_system) / Q_nutz
    """
    ts = extract_result_series(results)

    useful_heat = safe_series_sum(ts.get("heat_demand"))
    if useful_heat <= 0:
        return 0.0

    capex_total = capex_hp_total + capex_gas_boiler_total
    opex_sys = calculate_opex_system(
        results=results,
        electricity_price_per_kwh=electricity_price_per_kwh,
        gas_price_per_kwh=gas_price_per_kwh,
        electricity_price_series=electricity_price_series,
        gas_price_series=gas_price_series,
    )

    a = annuity_factor(interest_rate, lifetime)
    return ((capex_total * a) + opex_sys) / useful_heat


def calculate_performance_indicators(
    results,
    scenario_name: str,
    capex_ashp_kw: float = 1550,
    capex_gshp_kw: float = 2770,
    capex_wshp_kw: float = 1010,
    capex_solar_kw: float | None = None,
    capex_storage_total_eur: float | None = None,
    capex_gas_boiler_total: float = 0.0,
    electricity_price_per_kwh: float | None = None,
    gas_price_per_kwh: float | None = None,
    electricity_price_series: pd.Series | None = None,
    gas_price_series: pd.Series | None = None,
    lifetime: int = 20,
    interest_rate: float = 0.02,
) -> pd.DataFrame:
    """
    Berechnet zentrale techno-ökonomische Kennzahlen.
    """

    capex_hp = calculate_capex_hp(
        results=results,
        scenario_name=scenario_name,
        capex_ashp_kw=capex_ashp_kw,
        capex_gshp_kw=capex_gshp_kw,
        capex_wshp_kw=capex_wshp_kw,
        capex_solar_kw=capex_solar_kw,
        capex_storage_total_eur=capex_storage_total_eur,
    )

    opex_hp = calculate_opex_hp(
        results=results,
        electricity_price_per_kwh=electricity_price_per_kwh,
        electricity_price_series=electricity_price_series,
    )

    opex_sys = calculate_opex_system(
        results=results,
        electricity_price_per_kwh=electricity_price_per_kwh,
        gas_price_per_kwh=gas_price_per_kwh,
        electricity_price_series=electricity_price_series,
        gas_price_series=gas_price_series,
    )

    spf_hp = calculate_spf_hp(results)
    spf_system = calculate_spf_system(results)

    lcoh_hp = calculate_lcoh_hp(
        results=results,
        scenario_name=scenario_name,
        capex_ashp_kw=capex_ashp_kw,
        capex_gshp_kw=capex_gshp_kw,
        capex_wshp_kw=capex_wshp_kw,
        capex_solar_kw=capex_solar_kw,
        capex_storage_total_eur=capex_storage_total_eur,
        electricity_price_per_kwh=electricity_price_per_kwh,
        electricity_price_series=electricity_price_series,
        lifetime=lifetime,
        interest_rate=interest_rate,
    )

    lcoh_system = calculate_lcoh_system(
        results=results,
        capex_hp_total=capex_hp,
        capex_gas_boiler_total=capex_gas_boiler_total,
        electricity_price_per_kwh=electricity_price_per_kwh,
        gas_price_per_kwh=gas_price_per_kwh,
        electricity_price_series=electricity_price_series,
        gas_price_series=gas_price_series,
        lifetime=lifetime,
        interest_rate=interest_rate,
    )

    return pd.DataFrame([{
        "scenario": scenario_name,
        "capex_hp_eur": capex_hp,
        "opex_hp_eur_per_a": opex_hp,
        "opex_sys_eur_per_a": opex_sys,
        "spf_hp": spf_hp,
        "spf_system": spf_system,
        "lcoh_hp_eur_per_kwh": lcoh_hp,
        "lcoh_system_eur_per_kwh": lcoh_system,
    }])