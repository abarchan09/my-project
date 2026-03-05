from oemof import solph




def luft_heat_pump(es,el_bus,heat_bus,b_heat_bus,df):
    af=(0.02 * (1 + 0.02)**20) / ((1 + 0.02)**20 - 1)
    capex_sp=1550
    
    
    
    hp = solph.components.Converter(
        label="heat_pump",
        inputs={el_bus: solph.flows.Flow(),b_heat_bus:solph.flows.Flow()},
        outputs={heat_bus: solph.flows.Flow(
               nominal_capacity=solph.Investment(
                   ep_costs=capex_sp*af,
                   #minimum=100 
                   
               )
                    
                    
                  ),
            },
        conversion_factors={
            el_bus:1/df["COP"],b_heat_bus: (df["COP"]-1)/df["COP"]
              
        },
    )

    es.add(hp)
    
def sol_heat_pump(es,el_bus,heat_bus,b_heat_bus):
    af=(0.02 * (1 + 0.02)**20) / ((1 + 0.02)**20 - 1)
    capex_sp=2770
    
    hp= solph.components.Converter(
        label="heat_pump",
        inputs={el_bus: solph.flows.Flow(),b_heat_bus:solph.flows.Flow()},
        outputs={heat_bus: solph.flows.Flow(solph.Investment(
                   ep_costs=capex_sp*af)
             
                   
                   
                   
             ),
        
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


#----------------------------------------------------------------------------------#
#------SA-WSHP------------------------------------------#


def add_wasser_heat_pump(es,el_bus,heat_bus,water_bus,cop_series):
    
    hp = solph.components.Converter(
        label="heat_pump",
        inputs={el_bus: solph.flows.Flow(),water_bus:solph.flows.Flow()},
        outputs={heat_bus: solph.flows.Flow(
               nominal_capacity=solph.Investment(
                   ep_costs=50,
                   
               )
                    
                    
                  ),
            },
        conversion_factors={
            el_bus:1/cop_series, water_bus: (cop_series-1)/cop_series
              
        },
    )

    es.add(hp)
