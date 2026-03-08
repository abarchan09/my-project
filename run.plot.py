import pandas as pd
from plot import (
    plot_heat_demand,
    plot_temperature_and_cop,
    plot_temperature_and_ghi,
    plot_heat_demand_and_ghi,
    plot_cop_series,
    plot_multiple_cop,
)

df = pd.read_csv(r"C:\Users\chaml\Documents\code\bachelorarbeit-mohamed\daten\input_data.csv")
df["time"] = pd.to_datetime(df["time"])
df = df.set_index("time")

plot_heat_demand(df)

plot_temperature_and_cop(
    df,
    temp_col="temp_air",
    cop_col="COP",
    save_path=r"C:\Users\chaml\Documents\code\bachelorarbeit-mohamed\figuren\temp_cop.png"
)

plot_temperature_and_ghi(
    df,
    temp_col="temp_air",
    ghi_col="ghi"
)

plot_heat_demand_and_ghi(
    df,
    demand_col="heat_demand_kw",
    ghi_col="ghi"
)

plot_cop_series(
    df,
    cop_col="cop_wshp",
    y_min=3,
    y_max=4
)

plot_multiple_cop(
    df,
    cop_cols={
        "ASHP": "COP",
        "GSHP": "COP_GSHP",
        "SA-WSHP": "cop_wshp"
    }
)