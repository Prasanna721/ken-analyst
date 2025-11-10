import pandas as pd
from config import DATA_PATH

_df = None

def load_data():
    global _df
    _df = pd.read_csv(DATA_PATH)
    _df['symbol_lower'] = _df['symbol'].str.lower()
    _df['name_lower'] = _df['name'].str.lower()

def get_dataframe():
    return _df
