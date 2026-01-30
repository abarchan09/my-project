from oemof.solph import views
heat_bus_results = views.node(results, "heat_bus")
print(heat_bus_results["sequences"].head())