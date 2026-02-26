


def lcoh(opex,i,n,capex,e_menge):
      """
    Berechnet die Levelized Cost of heat (LCOh).

    capex   : Investitionskosten [€]
    opex    : Stromkosten
    i       : Zinssatz [-]
    n       : Lebensdauer [a]
    e_menge : jährlicher Energieertrag [kWh/a]
    Quelle: (vgl. Quaschning, Regenerative Energiesysteme)
    IEA.Projected Costs of Generating Electricity
    """
      if i == 0:
        a_capex = capex / n   # lineare Verteilung (Sonderfall)
      else:
        af = (i * (1 + i)**n) / ((1 + i)**n - 1)  # Annuitätenfaktor
        a_capex = capex * af

      return (a_capex+ opex) / e_menge

