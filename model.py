
from oemof import solph
from oemof.solph import create_time_index
from oemof.solph import views

from datanlesen import load_input_data
from src.source import add_pv,add_grid,add_heat_source
from src.sink import add_heat_demand,add_export,add_heat_dump
from src.converter import add_heat_pump
from config import load_config
from src.solver import solverin
from analysis.wirtschaft import calc_opex_lcoh
from analysis.ploten import plot_pv_grid_heatdemand

import pandas as pd




def bauen():
    
    print("1) Daten laden")
    df = load_input_data()
        

    print("2) Zeitindex erstellen")
    datetimeindex = create_time_index(2025,number=len(df))
    es = solph.EnergySystem(timeindex=datetimeindex,infer_last_interval=False)

    print("3)  Busse")
    el_bus = solph.Bus(label="strom")
    heat_bus = solph.Bus(label="waerme")
    b_heat_bus= solph.Bus(label="abwaerme")
    es.add(el_bus,heat_bus,b_heat_bus )    

    print("4) Source: pv,grid, heat_source")
    add_pv(es, el_bus, df)
    add_grid(es, el_bus,df)
    add_heat_source(es,b_heat_bus)
   

    print("5) Json aktivieren")
    cfg = load_config() 
    print("6) Sink: Heat demand, Export ")
    add_heat_demand(es,heat_bus,df)
    add_export(es,el_bus,df)
    add_heat_dump(es,heat_bus)

    print("7) Heat pump ")
    add_heat_pump(es,el_bus,heat_bus,b_heat_bus,cfg)

    

    print("✅ Build erfolgreich ")
    return es,df,cfg

if __name__ == "__main__":
    es,df,cfg = bauen()
    model,results= solverin(es)
    
    

    if results is None:
        print("❌ Modell infeasible")
    else:
        plot_pv_grid_heatdemand(results)

        opex, e_menge, lcoh_value = calc_opex_lcoh(results, df, cfg)
        print(f"OPEX: {opex:,.0f} €")
        print(f"Wärmemenge: {e_menge/1000:.1f} MWh")
        print(f"LCOH: {lcoh_value:.2f} €/kWh")
    