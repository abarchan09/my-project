from oemof import solph
from oemof.solph import create_time_index

from datanlesen import load_input_data
from src.source import add_pv
from src.sink import add_heat_demand
from config import load_config



def bauen():
    print("1) Zeitindex erstellen")
    timeindex = create_time_index(2025)

    print("2) Daten laden")
    input_data = load_input_data()

    print("3) EnergySystem & Busse")
    es = solph.EnergySystem(timeindex=timeindex)

    el_bus = solph.Bus(label="electricity")
    heat_bus = solph.Bus(label="heat")
    es.add(el_bus, heat_bus)

    print("3) Json aktivieren")
    cfg = load_config()    

    print("4) PV hinzufügen")
    add_pv(es, el_bus, cfg,input_data)

    print("5) Heat demand hinzufügen")
    add_heat_demand(es, heat_bus, input_data)

    

    print("✅ Build erfolgreich ")
    return es


if __name__ == "__main__":
    es = bauen()
