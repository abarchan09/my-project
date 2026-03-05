from oemof import solph
from oemof.solph import create_time_index

from datanlesen import load_input_data

# sources
from src.source import(
    add_pv,
    add_grid,
    add_gas_source,
    add_water_source
)

# sinks
from src.sink import (
    add_heat_demand,
    add_export
)

# converter
from src.converter import (
    add_gas_boiler,
    add_wasser_heat_pump
)

# solver
from src.solver import solverin

# analysis
from sa_wshp_analysis.views_sa_wshp import (
    extract_result_series,
    save_output_to_csv
)

from ag_analysis.ploten import plot_pv_grid_heatdemand



# COP Modell
from wsr.sa_wshp_cop import (
    cop_carnot_lift,
    compute_cop_series_for_area
)

from sa_wshp_analysis.plot_sa_wshp import (
    plot_area_sweep,
    plot_timeseries_one_case,
    plot_cop_series
)




def bauen(cop_series=None, A_m2_default=500):
    print("1) Daten laden")
    df = load_input_data()

    # wenn keine COP-Serie übergeben wurde, nutze Defaultfläche
    if cop_series is None:
        cop_series = compute_cop_series_for_area(
            df,
            A_m2=A_m2_default,
            T_source_C=10.0,
            T_sink_C=55.0,
            m_dot_kg_s=2.0,
            cp_J_kgK=4180.0,
            eta_carnot=0.5,
            T_source_max_C=35.0
        )

    print("2) Zeitindex erstellen")
    datetimeindex = create_time_index(2025, number=len(df))
    es = solph.EnergySystem(timeindex=datetimeindex, infer_last_interval=False)

    print("3) Busse")
    heat_bus = solph.Bus(label="waerme")
    el_bus   = solph.Bus(label="strom")
    water_bus= solph.Bus(label="water")
    gas_bus  = solph.Bus(label="gas")
    es.add(el_bus, heat_bus, gas_bus, water_bus)

    print("4) Sources")
    add_pv(es, el_bus, df)
    add_grid(es, el_bus, df)
    add_gas_source(es, gas_bus, df)
    add_water_source(es, water_bus)

    print("5) Sinks")
    add_heat_demand(es, heat_bus, df)
    add_export(es, el_bus, df)

    print("6) Converter")
    add_gas_boiler(es, gas_bus, heat_bus)
    add_wasser_heat_pump(es, el_bus, heat_bus, water_bus, cop_series)

    print("✅ Build erfolgreich")
    return es, df

if __name__ == "__main__":
    from sa_wshp_analysis.evalute_sa_wshp import run_area_sweep
    es, df = bauen()
    model, results, meta = solverin(es)

    if results is None:
        print("❌ Modell infeasible")
    else:
        output_data = extract_result_series(results)
        save_output_to_csv(output_data, "oemof_output")
        plot_pv_grid_heatdemand(output_data, rolling=True, window=168)

        areas_m2 = [ 800, 1200]
        df_sweep = run_area_sweep(df, areas_m2)
        df_sweep.to_csv("sa_wshp_area_sweep.csv", sep=";", index=False)
        print(df_sweep)

        cop_series = compute_cop_series_for_area(
            df,
            A_m2=500,
            T_source_C=10.0,
            T_sink_C=55.0,
            m_dot_kg_s=1.0,
            cp_J_kgK=4180.0,
            eta_carnot=0.5,
            T_source_max_C=35.0
        )

        plot_area_sweep(df_sweep, outdir="plots", prefix="sa_wshp")
        plot_timeseries_one_case(output_data, outdir="plots", prefix="sa_wshp_A500", rolling=True, window=168)
        plot_cop_series(cop_series, outdir="plots", prefix="sa_wshp_A500", rolling=True, window=168)


