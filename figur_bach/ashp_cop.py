import pandas as pd
import numpy as np 
import matplotlib.pyplot as plt


def cop_from_outdoor_temperature(
    T_air,
    T_ref=None,
    COP_ref=None,
    cop_min=1.5,
    cop_max=5.0,
    clamp=True,
    fill_method="ffill_bfill",
):
    """
    Calculate time-dependent COP(t) for an air-source heat pump based on
    outdoor air temperature (typical A/W55).

    Assumptions
    -----------
    - Air-source heat pump (ASHP)
    - Supply temperature approx. 55°C (radiator systems)
    - Linear interpolation between manufacturer test points
    - Test standard according to EN 14511

    Notes
    -----
    - If clamp=True, temperature values outside T_ref range are clipped to
      avoid extrapolation.
    - Missing values are filled (forward/backward) by default.

    Parameters
    ----------
    T_air : pandas.Series or array-like
        Outdoor air temperature in °C (time series). If Series, index is kept.

    T_ref : array-like, optional
        Reference outdoor temperatures (°C). Default: [-7, 2, 7, 12]

    COP_ref : array-like, optional
        COP at reference points (dimensionless). Default: [1.7, 2.1, 2.5, 2.9]

    cop_min, cop_max : float
        Physical bounds for COP clipping.

    clamp : bool
        If True, clip T_air to [min(T_ref), max(T_ref)] to avoid extrapolation.

    fill_method : {"ffill_bfill", "interpolate", None}
        How to handle NaNs/infs.

    Returns
    -------
    pandas.Series
        COP(t)
    """

    # Defaults
    if T_ref is None:
        T_ref = np.array([-7, 2, 7, 12], dtype=float)
    else:
        T_ref = np.array(T_ref, dtype=float)

    if COP_ref is None:
        COP_ref = np.array([1.7, 2.1, 2.5, 2.9], dtype=float)
    else:
        COP_ref = np.array(COP_ref, dtype=float)

    if T_ref.shape != COP_ref.shape:
        raise ValueError("T_ref and COP_ref must have the same length.")

    # Ensure Series for consistent handling
    if not isinstance(T_air, pd.Series):
        T_air = pd.Series(T_air)

    # Clean numeric
    T_air = pd.to_numeric(T_air, errors="coerce")
    T_air = T_air.replace([np.inf, -np.inf], np.nan)

    # Fill missing
    if fill_method == "ffill_bfill":
        T_air = T_air.ffill().bfill()
    elif fill_method == "interpolate":
        T_air = T_air.interpolate(limit_direction="both")
    elif fill_method is None:
        pass
    else:
        raise ValueError("fill_method must be 'ffill_bfill', 'interpolate', or None.")

    # If still NaNs remain -> raise (better than silent wrong COP)
    if T_air.isna().any():
        raise ValueError("T_air still contains NaNs after cleaning. Check input data.")

    T_vals = T_air.values.astype(float)

    # Avoid extrapolation if desired
    if clamp:
        T_vals = np.clip(T_vals, T_ref.min(), T_ref.max())

    # Interpolate COP
    cop_values = np.interp(T_vals, T_ref, COP_ref)

    # Optional: simple defrost penalty below 0°C (only if you want)
    # cop_values = np.where(T_air.values < 0, 0.95 * cop_values, cop_values)

    # Clip to bounds
    cop_values = np.clip(cop_values, cop_min, cop_max)

    return pd.Series(cop_values, index=T_air.index, name="COP")


def plot_cop_heating_period(cop_series, t_series,
                            T_thresh=15.0,
                            daily_mean=True):
    """
    Plot only COP during heating period (T_air < T_thresh).

    Parameters
    ----------
    cop_series : pandas.Series (COP)
    t_series   : pandas.Series (Außentemperatur in °C)
    T_thresh   : float (Heizgrenze, default 15°C)
    daily_mean : bool (True = Tagesmittel für glattere Kurve)
    """

    if not isinstance(cop_series.index, pd.DatetimeIndex):
        raise ValueError("Index must be DatetimeIndex")

    # Heizperioden-Maske
    mask = t_series < T_thresh
    cop_hp = cop_series[mask]

    # Optional glätten
    if daily_mean:
        cop_hp = cop_hp.resample("D").mean()

    # Plot
    plt.figure()
    plt.plot(cop_hp.index, cop_hp)
    plt.xlabel("Zeit")
    plt.ylabel("COP (-)")
    plt.title(f"COP in der Heizperiode (T < {T_thresh}°C)")
    plt.grid(True)
    plt.show()


# -------------------- Example usage --------------------

path = r"C:\Users\chaml\OneDrive\Documents\datenbank\daten\daten_quelle\wetter\weather_data.csv"

# WICHTIG: passe "time" an deine echte Zeitspalte an (z.B. "Time" / "timestamp")
df = pd.read_csv(path, parse_dates=["time"])
df = df.set_index("time")

# falls Temperatur in Kelvin ist:
T_air = df["temp_air"] - 273.15   # °C

cop_t = cop_from_outdoor_temperature(T_air)

plot_cop_heating_period(
    cop_series=cop_t,
    t_series=T_air,
    T_thresh=15,
    daily_mean=True
)

# Optional: Tagesmittel (ruhiger für Thesis)
cop_daily = cop_t.resample("D").mean()
T_daily = T_air.resample("D").mean()

cop_t.to_csv("cop_ashp_t.csv")


