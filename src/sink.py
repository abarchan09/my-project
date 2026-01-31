from oemof import solph



def add_heat_demand(es, heat_bus, df):
    
    

    


    demand = solph.components.Sink(
        label="last",
        inputs={
            heat_bus: solph.flows.Flow(
                nominal_value=df["heat_demand_kw"].max(),
                fix=df["heat_demand_kw"]/df["heat_demand_kw"].max(),

            )
        }
    )
    es.add(demand)
    
def add_export(es,el_bus):


   export = solph.components.Sink(
     label="export_to_grid",
     inputs={
        el_bus: solph.Flow(
            variable_costs=-0.05 
            )
     }
  )
   es.add(export)
def add_heat_dump(es,heat_bus):
     heat_dump = solph.components.Sink(
        label="heat_dump",
        inputs={heat_bus: solph.Flow(variable_costs=1000)
                }
             )
     
     es.add(heat_dump)
