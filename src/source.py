from oemof import solph





def add_pv(es, el_bus, df):
    """
    keine Kosten werden entstanden
    wenn enabled True ist, dann wird an modell addiert.
       """
    
    

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
    """strom preis aus dem  data
       export von strom bis Abdeckung der Last"""
    

    grid = solph.components.Source(
        label="el_grid",
        outputs={
            el_bus: solph.flows.Flow(
                nominal_capacity=500,
                
                variable_costs= df["el_price_eur_kwh"]+0.08,
                
                
                
                
            )
        }
    )

    es.add(grid)

def add_heat_source(es,b_heat_bus):
    air= solph.components.Source(label="heat_source",
                                  outputs={b_heat_bus: solph.flows.Flow()})
    es.add(air)
    

def add_backup_heat(es,heat_bus):
    backup_heat= solph.components.Source(
    label="backup_heat",
    outputs={heat_bus: solph.flows.Flow(variable_costs=0)})


    es.add(backup_heat)

