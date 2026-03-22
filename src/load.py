import pandas as pd 
import zipfile
import io

def load_file(path):
    if path.endswith('.csv'):
        return pd.read_csv(path)
    
    elif path.endswith('.xlsx'):
        return pd.read_excel(path)
    
    elif path.endswith('.parquet'):
        return pd.read_parquet(path)
    
    elif path.endswith('.zip'):
        with zipfile.ZipFile(path,'r') as z:
            file = z.namelist()[0]
            with z.open(file) as f:
                return pd.read_parquet(io.BytesIO(f.read()))
       
    else:        
        raise ValueError(f"Unsupported file format: {path}")