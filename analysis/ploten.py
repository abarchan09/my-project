import matplotlib.pyplot as plt
from oemof.solph import views



import matplotlib.pyplot as plt
from oemof.solph import views

def plot_pv_grid_heatdemand(results):
    # ---------- Strom-Bus ----------
    el_seq = views.node(results, "strom")["sequences"]
    grid = el_seq[(("el_grid", "strom"), "flow")]
    pv   = el_seq[(("pv_dach", "strom"), "flow")]

    # ---------- Wärme-Bus ----------
    heat_seq = views.node(results, "waerme")["sequences"]
    b_heat_seq = views.node(results, "abwaerme")["sequences"]

    heat_demand = heat_seq[(("waerme", "last"), "flow")]
    heat_source = b_heat_seq[(("abwaerme", "heat_pump"), "flow")]

    # ---------- Plot ----------
    fig, ax1 = plt.subplots(figsize=(12, 5))

    # Strom (linke Achse)
    ax1.plot(grid.index, grid.values, color="blue",  label="Grid (kW)")
    ax1.plot(pv.index,   pv.values,   color="green", label="PV (kW)")
    ax1.set_ylabel("Elektrische Leistung (kW)")
    ax1.set_xlabel("Zeit")
    ax1.grid(True, alpha=0.3)

    # Wärme (rechte Achse)
    ax2 = ax1.twinx()
    ax2.plot(heat_demand.index, heat_demand.values, color="red",    label="Heat demand (kW)")
    ax2.plot(heat_source.index, heat_source.values, color="yellow", label="Heat source (kW)")
    ax2.set_ylabel("Wärmeleistung (kW)")

    # Gemeinsame Legende (ax1 + ax2)
    lines = ax1.get_lines() + ax2.get_lines()
    labels = [l.get_label() for l in lines]
    ax1.legend(lines, labels, loc="upper right")

    plt.title("PV-, Netzstrom, Außenwärme und Wärmebedarf (FH Campus Modell)")
    plt.tight_layout()
    plt.show()


