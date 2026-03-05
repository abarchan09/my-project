
import pandas as pd
from oemof.solph import views

def extract_result_series(results) -> dict[str, pd.Series]:
    el_seq   = views.node(results, "strom")["sequences"]
    heat     = views.node(results, "waerme")
    heat_seq = heat["sequences"]
    gas_seq  = views.node(results, "gas")["sequences"]

    output_data = {
        # Strom
        "grid_import_el": el_seq[(("el_grid", "strom"), "flow")],
        "pv_el":          el_seq[(("pv_dach", "strom"), "flow")],
        "grid_export_el": el_seq[(("strom", "export_to_grid"), "flow")],

        # Gas
        "gas_import": gas_seq[(("gas_grid", "gas"), "flow")],

        # Wärme
        "hp_heat":     heat_seq[(("heat_pump", "waerme"), "flow")],
        "boiler_heat": heat_seq[(("gas_boiler", "waerme"), "flow")],
        "heat_demand": heat_seq[(("waerme", "last"), "flow")],
    }

    # --- Invest (kW) hinzufügen, falls vorhanden ---
    if "scalars" in heat:
        heat_scalars = heat["scalars"]

        # je nach solph-Version kann der Key leicht variieren
        invest_key = ((("heat_pump", "waerme"), "invest"))
        if invest_key in heat_scalars.index:
            output_data["cap_heat_pump_invest_kw"] = float(heat_scalars[invest_key])
        else:
            # fallback: manchmal ist es ein anderer Index-Typ
            try:
                output_data["cap_heat_pump_invest_kw"] = float(
                    heat_scalars.loc[invest_key]
                )
            except Exception:
                pass

    return output_data




def save_output_to_csv(output_data, filename_prefix="results"):

    timeseries_dict = {}
    scalar_dict = {}

    for key, value in output_data.items():
        if isinstance(value, pd.Series):
            timeseries_dict[key] = value
        else:
            scalar_dict[key] = value

    # ---- Zeitreihen speichern ----
    df_timeseries = pd.DataFrame(timeseries_dict)
    df_timeseries.to_csv(f"{filename_prefix}_timeseries_sa_wshp.csv", sep=";")

    # ---- Scalars speichern ----
    df_scalars = pd.DataFrame.from_dict(
        scalar_dict, orient="index", columns=["value"]
    )
    df_scalars.to_csv(f"{filename_prefix}_scalars_sa_wshp.csv", sep=";")

    print("CSV Dateien erfolgreich gespeichert.")