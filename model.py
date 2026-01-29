from oemof import solph
from oemof.solph import create_time_index

from datanlesen import load_input_data
from src.source import add_pv,add_grid
from src.sink import add_heat_demand
from src.converter import add_heat_pump
from config import load_config



def bauen():
    print("1) Zeitindex erstellen")
    timeindex = create_time_index(2025)

    print("2) Daten laden")
    data = load_input_data()

    print("3) EnergySystem & Busse")
    es = solph.EnergySystem(timeindex=timeindex)

    el_bus = solph.Bus(label="electricity")
    heat_bus = solph.Bus(label="heat")
    es.add(el_bus, heat_bus)

    print("3) Json aktivieren")
    cfg = load_config()    

    print("4) PV und grid hinzufügen")
    add_pv(es, el_bus,data)
    add_grid(es,el_bus,data)

    print("5) Heat demand hinzufügen")
    add_heat_demand(es, heat_bus, data)

    print("6 Heat pump hinzufügen")
    add_heat_pump(es,el_bus,heat_bus,data,cfg)

    

    print("✅ Build erfolgreich ")
    return es


if __name__ == "__main__":
    es = bauen()
