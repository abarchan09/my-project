from oemof import solph

def add_solar_thermie(es,b_heat_bus):
        st= solph.components.Source(label="solar_thermie",
                                     outputs={b_heat_bus:solph.flows.Flow(
                                             nominal_capacity=0,
                                             fix=0,
                                     )},
                                     )
        es.add(st)