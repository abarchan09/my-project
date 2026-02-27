import pandas as pd

df = pd.read_csv(
    "data.csv",
    index_col="time",
    parse_dates=["time"]
)

df["gas_price_euro_kWh"]=df["gas_price_euro_kWh"]*10
df.to_csv("data.csv")
# Dateien laden



