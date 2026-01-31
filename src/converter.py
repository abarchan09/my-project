import oemof.solph as solph




def add_heat_pump(es,el_bus,heat_bus,b_heat_bus,cfg):
    """
    COP als zeitrehe und von Temperatur abhängig,
    Änfingliche Investitionkosten
    

   
    """
    if not cfg["luft_hp"]["enabled"]:
        return None
    

    hp = solph.components.Converter(
        label="heat_pump",
        inputs={el_bus: solph.flows.Flow(),b_heat_bus:solph.flows.Flow()},
        outputs={heat_bus: solph.flows.Flow(
            nominal_value=cfg["luft_hp"]["nominal_value"],
            )},
        conversion_factors={
            el_bus: 1/3,
            b_heat_bus: (3-1)/3,  
        },
    )

    es.add(hp)
    


