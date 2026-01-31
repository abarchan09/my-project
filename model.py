
from oemof import solph
from oemof.solph import create_time_index
from oemof.solph import views

from datanlesen import load_input_data
from src.source import add_pv,add_grid,add_heat_source
from src.sink import add_heat_demand,add_export,add_heat_dump
from src.converter import add_heat_pump
from config import load_config
from src.solver import solverin
import pandas as pd




def bauen():
    
    print("1) Daten laden")
    df = load_input_data()
        

    print("2) Zeitindex erstellen")
    datetimeindex = create_time_index(2025,number=len(df))
    es = solph.EnergySystem(timeindex=datetimeindex,infer_last_interval=False)

    print("3)  Busse")
    el_bus = solph.Bus(label="strom")
    heat_bus = solph.Bus(label="wearme")
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
    add_export(es,el_bus)
    add_heat_dump(es,heat_bus)

    print("7) Heat pump ")
    add_heat_pump(es,el_bus,heat_bus,b_heat_bus,cfg)

    

    print("✅ Build erfolgreich ")
    return es

if __name__ == "__main__":
    es = bauen()
    model,results= solverin(es)
    
    

    if results is None:
        print("❌ Keine Results vorhanden (Modell nicht optimal / infeasible)")
    else:
        strom_bus_results = views.node(results, "strom")["sequences"]
        
        print(strom_bus_results.head())
    


    