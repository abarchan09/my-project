from oemof import solph



def add_heat_demand(es, heat_bus, data):
    
  


     demand = solph.components.Sink(
        label="last",
        inputs={
            heat_bus: solph.flows.Flow(
                nominal_value=data["heat_demand_kw"].max(),
                fix=data["heat_demand_kw"]/data["heat_demand_kw"].max(),
            )
        }
    )
     es.add(demand)
     return demand
