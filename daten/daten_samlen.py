import pandas as pd

path=r"C:\Users\chaml\Documents\code\bachelorarbeit-mohamed\daten\input_data_25.csv"
# --- df_1 laden ---
df_1 = pd.read_csv(
    path,
    index_col="time",
    parse_dates=["time"]
).sort_index()

path_w=r"C:\Users\chaml\Documents\code\bachelorarbeit-mohamed\figur_bach\weather_data.csv"

# --- df_2 laden (hat time-Spalte) ---
df_2 = pd.read_csv(path_w, parse_dates=["time"])
df_2 = df_2.set_index("time").sort_index()

# --- Zielindex: vollständige stündliche Zeitreihe für 2025 ---
full_index = pd.date_range("2025-01-01 00:00:00", "2025-12-30 22:00:00", freq="h")

# df_1 auf vollständigen Index bringen (fehlende Stunden werden NaN)
df_1 = df_1.reindex(full_index)

# --- Spalten aus df_2 sauber dazunehmen (Join nach Zeit) ---
df_1 = df_1.join(df_2[["profil"]], how="left")

# --- Fehlende Werte behandeln ---

df_1["solar_profil"] = df_1["profil"].ffill().bfill()     # COP sinnvoll auffüllen

# optional: Indexname wieder "time"
df_1.index.name = "time"

print(len(df_1), df_1.index.min(), df_1.index.max())
print(df_1[["solar_profil"]].isna().sum())

df_1.to_csv("input_data_25.csv")
