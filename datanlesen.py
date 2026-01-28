from pathlib import Path
import pandas as pd

DATA_DIR = Path(__file__).parent / "daten"

def load_input_data():
    """el_price in [€/kwh]
       heat demand in [kW]
       demand profil 0-1
       pv leistung in [kW]
       pv_profil     0-1
       cop abhängig von außentemp
       """
    df = pd.read_csv(
        DATA_DIR / "input_data.csv",
        index_col=0,
        parse_dates=True
    )
    return df

