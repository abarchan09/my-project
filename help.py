#----------kompresion Wärmepumpe
# Technisches Kennwert heatpump
# weleche Typ verwende ich für mein Senario??
def cop_ideal(t_senk,t_source):
    """ 
    ideal cop nach Carnot
    Wirkungsgrad ist gegeben
    t_senk und t_source in Celius
    quelle:H,Regenerative,8.3,384
    A2W35 EN 14511 """
    
    T_senk= pd.Series(t_senk)+273.15
    T_source= pd.Series(t_source)+273.15 
    cop=(T_senk/(T_senk-T_source))
    return
def jaz():
    """saesonal perfermonce VDI 4650
     Q_th : Wärmeenergie [kWh]
    W_el : elektrische Energie [kWh]
    quelle:H,Regenerative,8.5,384
    """
    return Q_th.sum()/ W_el.sum()
def cop_real(Q_demand,P):

    """ 
    Momentaner COP
    Q_dot : abgeführte Wärme [kW]
    P_el  : elektrische Leistung [kW]
    quelle:H,Regenerative,8.2,384
    """
    return Q_demand/P
def guetergrad():
    """quelle:H,Regenerative,8.4,384"""
    return (cop_ideal/cop_real)

# Investment kennwert

def lcoh(capex,opex,i,n,e_menge):
      """
    Berechnet die Levelized Cost of heat (LCOh).

    capex   : Investitionskosten [€]
    opex    : jährliche Betriebskosten [€/a]
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

      return (a_capex + opex) / e_menge

