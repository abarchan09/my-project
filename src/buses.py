from oemof import solph





def create_buses():
    """
    Erstellt alle für das Energiesystemmodell benötigten Busse.

    Die Busse dienen zur bilanziellen Verknüpfung der einzelnen
    Energiequellen, Umwandlungsprozesse und Senken. Für alle
    Szenarien wird eine einheitliche Busstruktur verwendet, um
    die Vergleichbarkeit der Ergebnisse sicherzustellen.

    Returns
    -------
    dict
        Dictionary mit allen Bus-Objekten.
    """

    buses = {
        # Elektrischer Energiesektor
        "electricity": solph.buses.Bus(label="electricity"),

        # Thermischer Endenergiebedarf (Gebäude)
        "heat": solph.buses.Bus(label="heat"),

        # Gasnetz
        "gas": solph.buses.Bus(label="gas"),

        # Niedertemperatur-Quellwärme (WP-Seite)
        "environmental_heat": solph.buses.Bus(label="environmental_heat"),

        # Solarthermische Wärme
        "solar_heat": solph.buses.Bus(label="solar_heat"),

        # Szenario 3
        "storage_heat":solph.buses.Bus(label="storage_heat"),
        "water": solph.buses.Bus(label="water"),
        

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