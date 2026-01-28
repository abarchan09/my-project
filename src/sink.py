from oemof import solph



def add_heat_demand(es, heat_bus, input_data):
  
   
    
   


    
    peak= input_data["heat_demand_kw"].max()

    

    demand = solph.components.Sink(
        label="last",
        inputs={
            heat_bus: solph.flows.Flow(
                nominal_value=peak,
                fix=input_data["heat_demand_kw"]/peak,
            )
        }
    )
    es.add(demand)
    return demand
