import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


def _ensure_outdir(outdir: str):
    if outdir:
        os.makedirs(outdir, exist_ok=True)


def plot_area_sweep(df_sweep: pd.DataFrame, outdir: str = "sa_wshp_plots", prefix: str = "sa_wshp"):
    """
    df_sweep muss Spalten enthalten (wie in run_area_sweep):
      - A_m2
      - LCOH_EUR_per_kWh
      - Total_cost_EUR
      - Q_th_MWh
      - optional: HP_cap_kW, COP_mean
      - optional: status ('ok'/'infeasible')
    """
    _ensure_outdir(outdir)

    # nur feasible
    dfp = df_sweep.copy()
    if "status" in dfp.columns:
        dfp = dfp[dfp["status"].astype(str).str.lower() == "ok"]

    dfp = dfp.sort_values("A_m2")

    # --- 1) A vs LCOH ---
    plt.figure()
    plt.plot(dfp["A_m2"], dfp["LCOH_EUR_per_kWh"], marker="o")
    plt.xlabel("Kollektorfläche A (m²)")
    plt.ylabel("LCOH (€/kWh_th)")
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(os.path.join(outdir, f"{prefix}_A_vs_LCOH.png"), dpi=200)
    plt.close()

    # --- 2) A vs Total_cost ---
    plt.figure()
    plt.plot(dfp["A_m2"], dfp["Total_cost_EUR"], marker="o")
    plt.xlabel("Kollektorfläche A (m²)")
    plt.ylabel("Gesamtkosten Zielfunktion (€/a)")
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(os.path.join(outdir, f"{prefix}_A_vs_TotalCost.png"), dpi=200)
    plt.close()

    # --- 3) A vs Wärmemenge ---
    plt.figure()
    plt.plot(dfp["A_m2"], dfp["Q_th_MWh"], marker="o")
    plt.xlabel("Kollektorfläche A (m²)")
    plt.ylabel("Jährliche Wärmemenge (MWh_th)")
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(os.path.join(outdir, f"{prefix}_A_vs_Qth.png"), dpi=200)
    plt.close()

    # --- optional 4) A vs HP_cap_kW ---
    if "HP_cap_kW" in dfp.columns and dfp["HP_cap_kW"].notna().any():
        plt.figure()
        plt.plot(dfp["A_m2"], dfp["HP_cap_kW"], marker="o")
        plt.xlabel("Kollektorfläche A (m²)")
        plt.ylabel("Investierte WP-Kapazität (kW_th)")
        plt.grid(True)
        plt.tight_layout()
        plt.savefig(os.path.join(outdir, f"{prefix}_A_vs_HPcap.png"), dpi=200)
        plt.close()

    # --- optional 5) A vs COP_mean ---
    if "COP_mean" in dfp.columns and dfp["COP_mean"].notna().any():
        plt.figure()
        plt.plot(dfp["A_m2"], dfp["COP_mean"], marker="o")
        plt.xlabel("Kollektorfläche A (m²)")
        plt.ylabel("Mittlerer COP (-)")
        plt.grid(True)
        plt.tight_layout()
        plt.savefig(os.path.join(outdir, f"{prefix}_A_vs_COPmean.png"), dpi=200)
        plt.close()


def plot_timeseries_one_case(output_data: dict, outdir: str = "sa_wshp_plots", prefix: str = "sa_wshp_case",
                             rolling: bool = True, window: int = 168):
    """
    output_data = dict aus extract_result_series(results)
    Erwartete Keys:
      - hp_heat
      - boiler_heat
      - heat_demand
      optional:
      - grid_import_el
      - pv_el
    """
    _ensure_outdir(outdir)

    df = pd.DataFrame({
        "hp_heat": output_data.get("hp_heat"),
        "boiler_heat": output_data.get("boiler_heat"),
        "heat_demand": output_data.get("heat_demand"),
    }).copy()

    # rolling glätten (z.B. 168h = 1 Woche)
    if rolling:
        dfp = df.rolling(window=window, min_periods=1).mean()
        suffix = f"_roll{window}"
    else:
        dfp = df
        suffix = ""

    # --- Wärmezeitreihen ---
    plt.figure()
    plt.plot(dfp.index, dfp["heat_demand"], label="Wärmelast")
    plt.plot(dfp.index, dfp["hp_heat"], label="WP Wärme")
    plt.plot(dfp.index, dfp["boiler_heat"], label="Gasboiler Wärme")
    plt.xlabel("Zeit")
    plt.ylabel("Leistung (kW)")
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    plt.savefig(os.path.join(outdir, f"{prefix}_heat_timeseries{suffix}.png"), dpi=200)
    plt.close()

    # --- Anteil-Plot (Stacked Area) optional ---
    # (nützlich für BA: "Deckungsanteile")
    plt.figure()
    hp = dfp["hp_heat"].fillna(0.0)
    gb = dfp["boiler_heat"].fillna(0.0)
    plt.stackplot(dfp.index, hp, gb, labels=["WP", "Gasboiler"])
    plt.plot(dfp.index, dfp["heat_demand"], label="Last", linewidth=1.0)
    plt.xlabel("Zeit")
    plt.ylabel("Leistung (kW)")
    plt.grid(True)
    plt.legend(loc="upper right")
    plt.tight_layout()
    plt.savefig(os.path.join(outdir, f"{prefix}_heat_stack{suffix}.png"), dpi=200)
    plt.close()


def plot_cop_series(cop: pd.Series, outdir: str = "sa_wshp_plots", prefix: str = "sa_wshp_case",
                    rolling: bool = True, window: int = 168):
    """
    cop: pd.Series (COP über Zeit)
    """
    _ensure_outdir(outdir)

    if rolling:
        cop_p = cop.rolling(window=window, min_periods=1).mean()
        suffix = f"_roll{window}"
    else:
        cop_p = cop
        suffix = ""

    plt.figure()
    plt.plot(cop_p.index, cop_p.values)
    plt.xlabel("Zeit")
    plt.ylabel("COP (-)")
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(os.path.join(outdir, f"{prefix}_COP{suffix}.png"), dpi=200)
    plt.close()