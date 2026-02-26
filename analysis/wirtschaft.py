from .help import lcoh
import pandas as pd

def calc_opex_lcoh(output_data, df, cfg):
    """
    data: dict aus extract_result_series(results)
    df: deine Input-Zeitreihe (el_price_eur_kwh, heat_demand_kw, ...)
    """
    
    grid_import = output_data["grid_import_el"]
    gas_import  = output_data["gas_import"]
    grid_export = output_data["grid_export_el"]
    cap_hp      = output_data["cap_heat_pump_invest"]  # investierte kW (oder kW_th)
    # ------------------ Prüfen --------------
    

    price = df["el_price_eur_kwh"]  # laut dir keine NaN


    # WICHTIG: auf grid_import Index bringen
    opex_tech = (grid_import * price).sum()
    
    
        
   

    # CAPEX [€]
    capex = cfg["sol_hp"]["capex_spezifisch"] * cap_hp

    # Wärmemenge [kWh] (wenn df stündlich und heat_demand_kw in kW)
    w_menge = output_data["hp_heat"].sum()

    lcoh_value = lcoh(
        opex_tech,
        0.02,
        20,
        capex,
        w_menge,
    )

    return opex_tech, capex, w_menge, lcoh_value

