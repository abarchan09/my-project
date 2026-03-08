import pandas as pd
path=r"C:\Users\chaml\Documents\code\bachelorarbeit-mohamed\figur_bach\weather_data.csv"

df=pd.read_csv(path)

df["profil"]=df["ghi"]/df["ghi"].max()

print(df.head(50))

df.to_csv(path)