import numpy as np
import pandas as pd


from src.solver import solverin
from sa_wshp_analysis.views_sa_wshp import extract_result_series
from wsr.sa_wshp_cop import compute_cop_series_for_area

def run_area_sweep(df, areas_m2):
    from sa_wshp_model import bauen
    rows = []

    for A in areas_m2:
        # 1) COP Serie (Solar → Quelltemp → COP)
        cop = compute_cop_series_for_area(
            df,
            A_m2=A,
            T_source_C=10.0,
            T_sink_C=55.0,
            m_dot_kg_s=2.0,
            cp_J_kgK=4180.0,
            eta_carnot=0.5,
            T_source_max_C=35.0
        )

        # 2) Build System mit diesem COP
        es, _ = bauen(cop_series=cop)   # wir passen bauen() gleich an
        model, results, meta = solverin(es)

        if results is None:
            rows.append({
                "A_m2": A,
                "status": "infeasible"
            })
            continue

        out = extract_result_series(results)

        # 3) Wärmemenge (kWh) – heat_demand ist eine Series in kW pro Stunde
        Q_th_kWh = float(out["heat_demand"].sum())

        # 4) Kosten aus meta (Zielfunktion)
        total_cost = float(meta["objective"])
        lcoh = total_cost / Q_th_kWh if Q_th_kWh > 0 else np.nan

        rows.append({
            "A_m2": A,
            "status": "ok",
            "COP_mean": float(cop.mean()),
            "COP_min": float(cop.min()),
            "COP_max": float(cop.max()),
            "Q_th_MWh": Q_th_kWh / 1000.0,
            "Total_cost_EUR": total_cost,
            "LCOH_EUR_per_kWh": float(lcoh),
        })

    return pd.DataFrame(rows)