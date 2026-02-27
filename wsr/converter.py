from oemof import solph

def waerme_tauscher(es,sol_bus,source_bus):
    hx = solph.components.Converter(
                label="heat_exchanger",
                inputs={sol_bus: solph.flows.Flow()},
                outputs={source_bus: solph.flows.Flow()},
                conversion_factors={source_bus: 0.9}
    )
    es.add(hx)

def wasser_heat_pump(es,el_bus,heat_bus,source_bus,cfg,df_sl):
    
    if not cfg["wasser_hp"]["enabled"]:
        return None
    
    hp = solph.components.Converter(
        label="heat_pump",
        inputs={el_bus: solph.flows.Flow(),source_bus:solph.flows.Flow()},
        outputs={heat_bus: solph.flows.Flow(
               nominal_capacity=solph.Investment(
                   ep_costs=cfg["wasser_hp"]["capex_spezifisch"],
                   
               )
                    
                    
                  ),
            },
        conversion_factors={
            el_bus:1/df_sl["COP_wshp"],source_bus: (df_sl["COP_wshp"]-1)/df_sl["COP_wshp"]
              
        },
    )

    es.add(hp)