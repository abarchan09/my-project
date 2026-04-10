import pandas as pd
from pathlib import Path
from oemof import solph

from src.scenario import build_scenario
from src.evaluate import calculate_summary, save_summary_to_csv, extract_result_series
from src.plot_model import plot_heat_supply_simple
from src.performance import calculate_performance_indicators


# ============================================================
# Daten einlesen
# ============================================================

def load_input_data(path: str, time_col: str = "time") -> pd.DataFrame:
    """
    Liest die Eingabedaten ein und setzt die Zeitspalte als Index.
    """
    path = Path(path)

    if not path.exists():
        raise FileNotFoundError(f"Datei nicht gefunden: {path}")

    df = pd.read_csv(path)

    if time_col not in df.columns:
        raise ValueError(f"Zeitspalte '{time_col}' wurde in der Datei nicht gefunden.")

    df[time_col] = pd.to_datetime(df[time_col], errors="coerce")
    df = df.dropna(subset=[time_col]).set_index(time_col).sort_index()

    if df.index.has_duplicates:
        raise ValueError("Der Zeitindex enthält doppelte Zeitstempel.")

    if len(df) == 0:
        raise ValueError("Die Eingabedatei enthält keine gültigen Daten.")

    return df


# ============================================================
# Modell ausführen
# ============================================================

def solve_scenario(df: pd.DataFrame, scenario_name: str, solver: str = "cbc"):
    """
    Baut und löst ein Szenario.

    Returns
    -------
    tuple
        es, buses, model, results, meta_results
    """
    es, buses = build_scenario(df, scenario_name)

    model = solph.Model(es)
    model.solve(solver=solver, solve_kwargs={"tee": False})

    results = solph.processing.results(model)
    meta_results = solph.processing.meta_results(model)

    return es, buses, model, results, meta_results


# ============================================================
# Meta-Ergebnisse speichern
# ============================================================

def save_meta_results(meta_results: dict, output_path: str):
    """
    Speichert Meta-Ergebnisse in einer Textdatei.
    """
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, "w", encoding="utf-8") as f:
        for key, value in meta_results.items():
            f.write(f"{key}: {value}\n")


# ============================================================
# Hauptprogramm
# ============================================================

if __name__ == "__main__":
    input_path = r"C:\Users\chaml\Documents\code\bachelorarbeit-mohamed\daten\input_data_25_with_cop.csv"
    output_dir = Path(r"C:\Users\chaml\Documents\code\bachelorarbeit-mohamed\results")
    scenario_name = "SA-WSHP"   # "ASHP", "GSHP", "SA-WSHP"
    solver_name = "cbc"

    output_dir.mkdir(parents=True, exist_ok=True)

    # 1. Daten laden
    df = load_input_data(input_path, time_col="time")

    # 2. Modell lösen
    es, buses, model, results, meta_results = solve_scenario(
        df=df,
        scenario_name=scenario_name,
        solver=solver_name,
    )

    print(f"Szenario {scenario_name} erfolgreich gelöst.\n")
    print("\n--- DEBUG: Heat Bus Flows ---")
    
    # 3. Meta-Ergebnisse speichern
    meta_path = output_dir / f"meta_results_{scenario_name}.txt"
    save_meta_results(meta_results, meta_path)

    print("Meta-Ergebnisse:")
    for key, value in meta_results.items():
        print(f"{key}: {value}")

    # 4. Summary berechnen
    summary_df = calculate_summary(results, scenario_name)

    print("\nSummary:")
    print(summary_df)

    # 5. Summary speichern
    summary_path = output_dir / f"summary_neu_{scenario_name}.csv"
    save_summary_to_csv(summary_df, summary_path)

    print(f"\nSummary gespeichert unter: {summary_path}")
    print(f"Meta-Ergebnisse gespeichert unter: {meta_path}")

    # 6. Zeitreihen extrahieren und plotten
    output_data = extract_result_series(results)
    plot_heat_supply_simple(
        output_data,
        rolling=True,
        window=168,
        save_path=str(output_dir / f"betriebsverhalten_{scenario_name}.svg")
    )

    # 7. Performance-Indikatoren berechnen
    performance_df = calculate_performance_indicators(
        results=results,
        scenario_name=scenario_name,
        capex_ashp_kw=1550,
        capex_gshp_kw=2770,
        capex_wshp_kw=1010,
        capex_solar_kw=360,                 # falls Solarthermie in €/kW bewertet wird
        capex_storage_total_eur=5100,       # fester Speicher-CAPEX
        capex_gas_boiler_total=0.0,
        electricity_price_per_kwh=0.20,
        gas_price_per_kwh=0.12,
        lifetime=20,
        interest_rate=0.02,
    )

    performance_path = output_dir / f"performance_{scenario_name}.csv"
    performance_df.to_csv(performance_path, index=False, encoding="utf-8-sig")

    print(f"Performance-Ergebnisse gespeichert unter: {performance_path}")
    print("\nPerformance:")
    print(performance_df)