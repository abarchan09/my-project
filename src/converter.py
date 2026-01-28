import oemof.solph as solph




def add_heat_pump(
    es: solph.EnergySystem,
    el_bus: solph.Bus,
    heat_bus: solph.Bus,
    cop_t,
    cfg: dict
):
    """
    Add a heat pump as Converter: electricity -> heat with time-varying COP.

   
    """
    if not cfg.get("enabled", True):
        return None

    # Flow on heat output: either fixed size (nominal_value) or investable
    heat_flow_kwargs = {}

    mode = cfg.get("mode", "fixed")  # "fixed" or "investment"

    if mode == "fixed":
        heat_flow_kwargs["nominal_value"] = float(cfg["nominal_value_kw"])
    elif mode == "investment":
        inv = solph.Investment(
            ep_costs=float(cfg["capex_eur_per_kw"]),
            maximum=float(cfg.get("maximum_kw", 1e9)),
            lifetime=int(cfg.get("lifetime", 20)),
        )
        heat_flow_kwargs["investment"] = inv
    else:
        raise ValueError(f"Unknown heat_pump mode: {mode}")

    # Optional annual fixed OPEX per kW (maintenance etc.)
    if "fixed_costs_eur_per_kw_a" in cfg:
        heat_flow_kwargs["fixed_costs"] = float(cfg["fixed_costs_eur_per_kw_a"])

    hp = solph.components.Converter(
        label="heat_pump",
        inputs={el_bus: solph.flows.Flow()},
        outputs={heat_bus: solph.flows.Flow(**heat_flow_kwargs)},
        conversion_factors={
            el_bus: 1.0,
            heat_bus: cop_t,   # time-varying COP
        },
    )

    es.add(hp)
    return hp


