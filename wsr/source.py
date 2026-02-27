from oemof import solph

def add_solar_thermie(es,sol_bus,df_sl):
        st= solph.components.Source(label="solar_thermie",
                                     outputs={sol_bus:solph.flows.Flow(
                                             nominal_capacity=df_sl["solar_th_kw"]
                                     )},
                                     )
        es.add(st)