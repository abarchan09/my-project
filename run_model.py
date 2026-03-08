import pandas as pd
from pathlib import Path
from oemof import solph

from src.scenario import build_scenario
from src.evaluate import calculate_summary, save_summary_to_csv
from src.plot_model import plot_heat_supply
from src.evaluate import extract_result_series

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
    Rückgabe:
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
    input_path = r"C:\Users\chaml\Documents\code\bachelorarbeit-mohamed\daten\input_data_25.csv"
    output_dir = Path(r"C:\Users\chaml\Documents\code\bachelorarbeit-mohamed\results")
    scenario_name = "SA-WSHP"  # "ASHP", "GSHP", "SA-WSHP"
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
    summary_path = output_dir / f"summary_{scenario_name}.csv"
    save_summary_to_csv(summary_df, summary_path)

    print(f"\nSummary gespeichert unter: {summary_path}")
    print(f"Meta-Ergebnisse gespeichert unter: {meta_path}")
    
    from src.evaluate import extract_result_series
    from src.plot_model import plot_heat_supply_simple

    output_data = extract_result_series(results)
    plot_heat_supply_simple(output_data, rolling=True, window=168)
    

