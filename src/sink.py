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
    
