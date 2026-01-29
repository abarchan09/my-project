from oemof import solph




def add_pv(es, el_bus, data):
    """
    keine Kosten werden entstanden
    wenn enabled True ist, dann wird an modell addiert.
       """
    
    

    pv = solph.components.Source(
        label="pv_dach",
        outputs={
            el_bus: solph.flows.Flow(
                nominal_value=data["pv_power_kw"].max(),
                fix= data["pv_power_kw"]/data["pv_power_kw"].max(),
                
                
            )
        }
    )

    es.add(pv)
    return pv

def add_grid(es, el_bus,data):
    """strom preis aus dem  data
       export von strom bis Abdeckung der Last"""
    

    grid = solph.components.Source(
        label="el_grid",
        outputs={
            el_bus: solph.flows.Flow(
                variable_costs= data["el_price_eur_kwh"],
                
            )
        }
    )

    es.add(grid)
    return grid


