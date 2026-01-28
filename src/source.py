from oemof import solph




def add_pv(es, el_bus, cfg,input_data):
    """nominal_value [kW]
       pv profil aus dem Inputdata
       sp_capex :spezifisch betrieb kosten [€/kW_p]"""
    
    if not cfg["pv"]["enabled"]:
        return None

    pv = solph.components.Source(
        label="pv_installation",
        outputs={
            el_bus: solph.flows.Flow(
                nominal_value=cfg["pv"]["nominal_value"],
                fix=input_data["pv_power_kw"]/cfg["pv"]["nominal_value"],
                
                
            )
        }
    )

    es.add(pv)
    return pv

def add_grid(es, el_bus, el_price, cfg):
    """strom preis aus dem input_data
       export von strom bis Abdeckung der Last"""
    if not cfg["enabled"]:
        return None

    grid = solph.components.Source(
        label="el_grid",
        outputs={
            el_bus: solph.flows.Flow(
                variable_costs=input_data["el_price_eur_kwh"],
                
            )
        }
    )

    es.add(grid)
    return grid


