from oemof import solph

def solverin(es, solver="cbc"):
    model = solph.Model(energysystem=es)
    try:
        model.solve(solver=solver,allow_nonoptimal=False, solve_kwargs={"tee": True, "keepfiles": False})
    except RuntimeError as e:
        print("❌ Nicht optimal:", e)
        # Hier KEIN results, weil infeasible
        return model, None

    results = solph.processing.results(model)
    print("✅ Optimal gelöst")
    return model, results






