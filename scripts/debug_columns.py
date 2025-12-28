
import pandas as pd
from pathlib import Path

def analyze_columns(data_dir):
    data_path = Path(data_dir)
    files = list(data_path.glob("*.xls"))
    
    all_columns = {}
    
    for file_path in files:
        if "Consulta_Base_Unificada" not in file_path.name and "Reporte_Bases" not in file_path.name:
            continue
            
        print(f"Reading {file_path.name}...")
        df = pd.read_excel(file_path, nrows=5)
        all_columns[file_path.name] = list(df.columns)
        
    return all_columns

if __name__ == "__main__":
    BASE_DIR = Path(r"c:\Users\franc\OneDrive\Escritorio\Mis Cosas\Prob Leads - Data Science Nods")
    columns_map = analyze_columns(BASE_DIR / "data")
    
    # Print all columns for each university
    for filename, cols in columns_map.items():
        print(f"\n--- {filename} ---")
        for col in sorted(cols):
            print(f"  {col}")
