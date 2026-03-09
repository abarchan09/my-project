import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


# -----------------------------
# COP Modell
# -----------------------------
def cop_carnot_lift(T_source_C=10.0, T_sink_C=55.0, eta_carnot=0.5):
    Tc = T_source_C + 273.15
    Th = T_sink_C + 273.15

    delta_T = Th - Tc
    delta_T = np.maximum(delta_T, 1e-6)

    cop = eta_carnot * (Th / delta_T)

    return np.clip(cop, 2.0, 8.0)


def compute_cop_series_sa_wshp(
    df,
    T_source_C=10.0,
    T_sink_C=55.0,
    m_dot_kg_s=6.0,
    cp_J_kgK=4180.0,
    eta_carnot=0.5,
    T_source_max_C=35.0,
    smooth_hours=48,
    Qsol_max_kW=30.0
):
    df = df.copy()

    # Rohdaten
    solar_q_raw = pd.to_numeric(df["solar_profil"], errors="coerce").fillna(0.0).clip(lower=0.0)

    # Glättung
    solar_q_smooth = solar_q_raw.ewm(span=smooth_hours, adjust=False).mean()

    # Normiertes Solarprofil
    

    solar_profile = solar_q_smooth 

    # Maximale Solarwärmeleistung [W]
    Qsol_max_W = Qsol_max_kW * 1000.0

    # Zeitabhängige Solarwärmeleistung [W]
    Qsol_W = Qsol_max_W * solar_profile

    # Temperaturerhöhung im Quellkreis
    dT_K = Qsol_W / (m_dot_kg_s * cp_J_kgK)

    # Vorgewärmte Quellentemperatur
    T_pre_C = T_source_C + dT_K
    T_pre_C = np.minimum(T_pre_C, T_source_max_C)

    # COP
    cop = cop_carnot_lift(T_pre_C, T_sink_C=T_sink_C, eta_carnot=eta_carnot)

    # Ergebnisse
    df["solar_q_Wm2_smooth"] = solar_q_smooth
    
    df["Qsol_W"] = Qsol_W
    df["dT_K"] = dT_K
    df["T_pre_C"] = T_pre_C
    df["COP_wshp"] = cop

    return df


# -----------------------------
# CSV Datei laden
# -----------------------------
path = r"C:\Users\chaml\Documents\code\bachelorarbeit-mohamed\daten\input_data_25.csv"

df = pd.read_csv(path)

time_candidates = ["time", "Time", "datetime", "DateTime", "timestamp", "Timestamp", "date", "Date"]
time_col = next((c for c in time_candidates if c in df.columns), None)

if time_col is not None:
    df[time_col] = pd.to_datetime(df[time_col], errors="coerce")
    df = df.dropna(subset=[time_col]).set_index(time_col).sort_index()

# -----------------------------
# COP berechnen für 150 kW Solarthermie
# -----------------------------
df_res = compute_cop_series_sa_wshp(
    df,
    T_source_C=10.0,
    T_sink_C=55.0,
    m_dot_kg_s=6.0,
    cp_J_kgK=4180.0,
    eta_carnot=0.5,
    T_source_max_C=35.0,
    smooth_hours=48,
    Qsol_max_kW=30.0
)

# Plot
plt.figure(figsize=(12, 4))
plt.plot(df_res.index, df_res["COP_wshp"], linewidth=0.8)
plt.ylabel("COP [-]")
plt.xlabel("Zeit")
plt.title("COP der SA-WSHP bei 30 kW Solarthermie")
plt.grid(alpha=0.3)
plt.tight_layout()
plt.show()

#df["cop_wshp"] = df_res["COP_wshp"].values
#df.to_csv(path, index=True)

