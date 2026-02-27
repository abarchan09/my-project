from oemof import solph




def luft_heat_pump(es,el_bus,heat_bus,b_heat_bus,cfg,df):
    
    if not cfg["luft_hp"]["enabled"]:
        return None
    
    hp = solph.components.Converter(
        label="heat_pump",
        inputs={el_bus: solph.flows.Flow(),b_heat_bus:solph.flows.Flow()},
        outputs={heat_bus: solph.flows.Flow(
               nominal_capacity=solph.Investment(
                   ep_costs=cfg["luft_hp"]["capex_spezifisch"],
                   
               )
                    
                    
                  ),
            },
        conversion_factors={
            el_bus:1/df["COP"],b_heat_bus: (df["COP"]-1)/df["COP"]
              
        },
    )

    es.add(hp)
    
def sol_heat_pump(es,el_bus,heat_bus,b_heat_bus,cfg):
    if not cfg["sol_hp"]["enabled"]:
        return None
    hp= solph.components.Converter(
        label="heat_pump",
        inputs={el_bus: solph.flows.Flow(),b_heat_bus:solph.flows.Flow()},
        outputs={heat_bus: solph.flows.Flow(
             nominal_capacity=solph.Investment(
                   ep_costs=cfg["sol_hp"]["ep"],
                   
                   
             ),
        )
            },
        conversion_factors={
            el_bus: 1/3.5,
            b_heat_bus: 3.5-1/3.5,  
        },
    )
    es.add(hp)



def add_gas_boiler(es,gas_bus,heat_bus):
    gasboiler= solph.components.Converter(
        label="gas_boiler",
        inputs={gas_bus:solph.flows.Flow()},
        outputs={heat_bus:solph.flows.Flow()},
        conversion_factors={gas_bus:0.9
                            }
    )
    es.add(gasboiler)



