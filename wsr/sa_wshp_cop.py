import numpy as np
import pandas as pd


def cop_carnot_lift(T_source_C=10, T_sink_C=55.0, eta_carnot=0.5):
    """
    Einfaches COP-Modell über Carnot-Faktor.
    - T_source_C kann Zeitreihe sein (°C)
    - T_sink_C konstant (55°C)
    """
    Tc = (T_source_C + 273.15)
    Th = (T_sink_C + 273.15)

    # Carnot COP (Heizen): Th / (Th - Tc)
    cop = eta_carnot * (Th / (Th - Tc))

    # Robust clamp (damit es nicht explodiert bei kleinen Lifts)
    return np.clip(cop, 2.0, 8.0)


def compute_cop_series_for_area(
    df,
    A_m2,
    T_source_C=10.0,
    T_sink_C=55.0,
    m_dot_kg_s=2.0,
    cp_J_kgK=4180.0,
    eta_carnot=0.5,
    T_source_max_C=35.0
):
    """
    Solarthermie erwärmt den Quellkreis:
    Qsol_W = A * solar_q_Wm2
    dT_K   = Qsol_W / (m_dot * cp)
    T_pre  = T_source_C + dT
    COP(t) = f(T_pre, T_sink)
    """
    Qsol_W = A_m2 * df["solar_q_Wm2"].clip(lower=0.0)  # W
    dT_K = Qsol_W / (m_dot_kg_s * cp_J_kgK)           # K (= °C Differenz)

    T_pre_C = T_source_C + dT_K
    T_pre_C = np.minimum(T_pre_C, T_source_max_C)     # optional: Begrenzung

    cop = cop_carnot_lift(T_pre_C, T_sink_C=T_sink_C, eta_carnot=eta_carnot)
    return pd.Series(cop, index=df.index, name="COP_wshp")

