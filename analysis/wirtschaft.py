from oemof.solph import views



def calc_opex_lcoh(results, df, cfg):
    # Strombus
    strom_bus = views.node(results, "strom")["sequences"]

    # Netzimport (exakter Key aus deiner Ausgabe)
    grid_import = strom_bus[(("el_grid", "strom"), "flow")]
    
    #Netz_export

    grid_export= strom_bus[(("strom","export_to_grid"),"flow")]


    # OPEX [€]
    opex = (grid_import * (df["el_price_eur_kwh"] + 0.08)).sum()-(grid_export*(df["el_price_eur_kwh"] + 0.08)).sum()

    # Wärmemenge [kWh] → falls df stündlich
    e_menge_kwh = df["heat_demand_kw"].sum()

    from .help import lcoh
    lcoh_value = lcoh(
        opex,
        cfg["luft_hp"]["capex"],
        cfg["luft_hp"]["lebensdauer"],
        cfg["luft_hp"]["zinsen"],
        e_menge_kwh,
    )

    return opex, e_menge_kwh, lcoh_value

