from oemof import solph

def add_puffer_speicher(es,b_heat_bus):
    w_speicher=solph.components.GenericStorage(label="tank",
                                               nominal_capacity=0,
                                               inputs={b_heat_bus:solph.flows.Flow()},
                                               outputs={b_heat_bus:solph.flows.Flow()},
                                               loss_rate=0,
                                               initial_storage_level=0,
                                               max_storage_level=0,
                                               inflow_conversion_factor=0,
                                               outflow_conversion_factor=0,
                                               )
    es.add(w_speicher)