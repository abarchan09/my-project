
from oemof import solph
from oemof.solph import create_time_index


from datanlesen import load_input_data
from src.source import add_pv,add_grid,add_heat_source,add_gas_source
from src.sink import add_heat_demand,add_export,add_heat_dump
from src.converter import luft_heat_pump,sol_heat_pump,add_gas_boiler
from config import load_config
from src.solver import solverin
from analysis.views import extract_result_series,save_output_to_csv
from analysis.wirtschaft import calc_opex_lcoh
from analysis.ploten import plot_pv_grid_heatdemand






def bauen():
    
    print("1) Daten laden")
    df = load_input_data()
    
        

    print("2) Zeitindex erstellen")
    datetimeindex = create_time_index(2025,number=len(df))
    es = solph.EnergySystem(timeindex=datetimeindex,infer_last_interval=False)

    print("3)  Busse")
    
    heat_bus= solph.Bus(label="waerme")
    el_bus = solph.Bus(label="strom")
    
    b_heat_bus= solph.Bus(label="abwaerme")
    gas_bus= solph.Bus(label="gas")
    es.add(el_bus,heat_bus,b_heat_bus,gas_bus )    

    print("4) Source: pv,grid, heat_source")
    add_pv(es, el_bus, df)
    add_grid(es, el_bus,df)
    add_heat_source(es,b_heat_bus)
    add_gas_source(es,gas_bus,df)
   

    print("5) Json aktivieren")
    cfg = load_config() 
    print("6) Sink: Heat demand, Export ")
    add_heat_demand(es,heat_bus,df)
    add_export(es,el_bus,df)
    add_heat_dump(es,heat_bus)

    print("7) Heat pump ")
    luft_heat_pump(es,el_bus,heat_bus,b_heat_bus,cfg,df)
    sol_heat_pump(es,el_bus,heat_bus,b_heat_bus,cfg)
    add_gas_boiler(es,gas_bus,heat_bus)


    

    print("✅ Build erfolgreich ")
    return es,df,cfg

if __name__ == "__main__":
    es,df,cfg = bauen()
    model,results= solverin(es)
    
    

    if results is None:
        print("❌ Modell infeasible")
    else:
        output_data = extract_result_series(results)   
        save_output_to_csv(output_data, "oemof_output")
        plot_pv_grid_heatdemand(output_data, rolling=True, window=168)
        opex_tech, capex, w_menge, lcoh_val = calc_opex_lcoh(output_data, df, cfg)

        

        

      
        
        
        print(f"OPEX: {opex_tech:,.3f} €")
        print(f"CAPEX:{capex:,.0f} €")
        print(f"Wärmemenge: {w_menge/1000000:.3f} GWh")
        print(f"LCOH: {lcoh_val:.2f} €/kWh")
    