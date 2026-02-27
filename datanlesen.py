from pathlib import Path
import pandas as pd

DATA_DIR = Path(__file__).parent / "daten"

def load_input_data():
    
    
    df= pd.read_csv(DATA_DIR/"input_data.csv",
                      index_col=0,
                      parse_dates=True
                      )
    df_sol=pd.read_csv(DATA_DIR/"cop_wshp.csv",
                      index_col=0,
                      parse_dates=True)
    
    return df , df_sol

