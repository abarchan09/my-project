from pathlib import Path
import pandas as pd

DATA_DIR = Path(__file__).parent / "daten"

def load_input_data():
    
    
    df= pd.read_csv(DATA_DIR/"data.csv",
                      index_col=0,
                      parse_dates=True
                      )
    
    return df

