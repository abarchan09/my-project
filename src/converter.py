import oemof.solph as solph




def add_heat_pump(es,el_bus,heat_bus,data,cfg):
    """
    COP als zeitrehe und von Temperatur abhängig,
    Änfingliche Investitionkosten
    

   
    """
    if not cfg["luft_hp"]["enabled"]:
        return None

    hp = solph.components.Converter(
        label="heat_pump",
        inputs={el_bus: solph.flows.Flow()},
        outputs={heat_bus: solph.flows.Flow(
            nominal_value=cfg["luft_hp"]["nominal_value"],
            fix=1,)},
        conversion_factors={
            el_bus: 1/data["cop_t"],
            heat_bus: 1,  
        },
    )

    es.add(hp)
    return hp


