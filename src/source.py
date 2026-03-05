from oemof import solph





def add_pv(es, el_bus, df):
    
    
    pv = solph.components.Source(
        label="pv_dach",
        outputs={
            el_bus: solph.flows.Flow(
                nominal_capacity=df["PV_kw"].max(),
                fix= df["PV_kw"]/df["PV_kw"].max(),
                
            )
        }
    )

    es.add(pv)
    

def add_grid(es, el_bus,df):
    
    
    grid = solph.components.Source(
        label="el_grid",
        outputs={
            el_bus: solph.flows.Flow(
                
                variable_costs= df["el_price_eur_kwh"],
                 
            )
        }
    )

    es.add(grid)

def add_heat_source(es,b_heat_bus):
    umwelt= solph.components.Source(label="heat_source",
                                  outputs={b_heat_bus: solph.flows.Flow()})
    es.add(umwelt)
    



def add_gas_source(es,gas_bus,df):
    gas= solph.components.Source(label="gas_grid",
                                 outputs={gas_bus:solph.flows.Flow(
                                     variable_costs=df["gas_price"],
                                     
                                     )})
    es.add(gas)

#---------------------------------------------------------------------#
#-------- Wasser solarthermie------------------#

def add_solar_thermie(es,sol_bus,df):

        st= solph.components.Source(label="solar_thermie",
                                outputs={sol_bus:solph.flows.Flow(
                                             nominal_capacity=solph.Investment(
                                                  ep_costs=70
                                             ),       
                                             fix=df["solar_q_Wm2"],)
                                             
                                     
                                     }
                                     )
        es.add(st)

def add_water_source(es, water_bus):
    wt = solph.components.Source(
        label="water_source",
        outputs={water_bus: solph.flows.Flow(variable_costs=0.0)}
    )
    es.add(wt)