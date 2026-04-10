from oemof import solph


def add_puffer_speicher(es, buses: dict):
    """
    Fügt einen thermischen Pufferspeicher als GenericStorage hinzu.

    Der Speicher nimmt Wärme aus dem Solarthermie-Bus auf und gibt sie
    an den Bus der Quellwärme für die Wärmepumpe ab.

    Annahmen:
    - Speichervolumen: 500 l
    - Tmax: 95 °C
    - Tmin: 30 °C
    - Bereitschaftswärmeverlust: 1.7 kWh/24h
    - Investitionskosten gesamt: 5100 €
    - Annuitätsfaktor: 0.0612
    """

    #  input Busse
    b_water = buses["water"]
              
    
    #output  
    b_env_heat = buses["environmental_heat"] # Entladung
    # Parameter
    volume_l = 500       # Liter
    t_max = 55              #grad
    t_min = 30
    standby_loss_per_day = 1.7   # kWh/24h
    capex_total = 5100      # €
    annuity_factor = 0.0612

    # Nutzbare Speicherkapazität [kWh]
    delta_t = t_max - t_min
    storage_capacity_kwh = volume_l * 4.18 * delta_t / 3600

    # Relative stündliche Verlustquote [-]
    standby_loss_per_hour = standby_loss_per_day / 24
    loss_rate = standby_loss_per_hour / storage_capacity_kwh

    # Annuitisierte spezifische Investitionskosten [€/kWh*a]
    ep_costs = (capex_total * annuity_factor) / storage_capacity_kwh

    storage = solph.components.GenericStorage(
        label="pufferspeicher",
        nominal_storage_capacity=solph.Investment(
                  ep_costs=ep_costs),
        
        inputs={
            b_water: solph.flows.Flow(),
           
        },
        outputs={
            b_env_heat: solph.flows.Flow()
            
        },
        loss_rate=loss_rate,
        inflow_conversion_factor=0.99,
        outflow_conversion_factor=0.99,
    )

    es.add(storage)
    return storage