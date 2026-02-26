import pandas as pd

df = pd.read_csv(
    "data.csv",
    index_col="time",
    parse_dates=["time"]
)
df.to_csv("data.csv")
# Dateien laden



