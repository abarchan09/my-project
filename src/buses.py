from oemof import solph


def create_buses():
    """
    Erstellt alle für das Energiesystemmodell benötigten Busse.

    Die Busse dienen zur bilanziellen Verknüpfung der einzelnen
    Energiequellen, Wandler und Senken. Für alle Szenarien wird
    eine einheitliche Bus-Struktur verwendet, um die Vergleichbarkeit
    der Ergebnisse sicherzustellen.

    Returns
    -------
    dict
        Dictionary mit allen Bus-Objekten.
    """
    buses = {
        "electricity": solph.buses.Bus(label="electricity"),
        "heat": solph.buses.Bus(label="heat"),
        "gas": solph.buses.Bus(label="gas"),
        "ambient_heat": solph.buses.Bus(label="ambient_heat"),
        "ground_heat": solph.buses.Bus(label="ground_heat"),
        "water_heat": solph.buses.Bus(label="water_heat"),
    }

    return buses


def add_buses_to_system(es, buses: dict):
    """
    Fügt alle Busse dem oemof-Energiesystem hinzu.

    Parameters
    ----------
    es :
        oemof EnergySystem
    buses : dict
        Dictionary mit Bus-Objekten
    """
    es.add(*buses.values())