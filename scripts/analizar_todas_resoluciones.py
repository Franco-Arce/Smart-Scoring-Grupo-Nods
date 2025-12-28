"""
Análisis exhaustivo de valores de Resolución en TODAS las universidades
"""
import pandas as pd
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data"

universidades = {
    'UNAB': DATA_DIR / 'Consulta_Base_Unificada_UNAB.xls',
    'Crexe': DATA_DIR / 'Reporte_Bases_Unificadas_Crexe.xls',
    'UEES': DATA_DIR / 'Consulta_Base_Unificada_UEES.xls',
    'Anahuac': DATA_DIR / 'Consulta_Base_Unificada_Anahuac.xls',
    'Unisangil': DATA_DIR / 'Consulta_Base_Unificada_Unisangil.xls'
}

print("="*100)
print("ANALISIS DE VALORES DE RESOLUCION POR UNIVERSIDAD")
print("="*100)

todos_valores = {}

for nombre, archivo in universidades.items():
    if archivo.exists():
        print(f"\n{'='*100}")
        print(f"UNIVERSIDAD: {nombre}")
        print(f"{'='*100}")
        
        df = pd.read_excel(archivo)
        
        # Buscar columna de resolución (puede tener espacios)
        cols_resolucion = [c for c in df.columns if 'resolucion' in c.lower() or 'resolución' in c.lower()]
        
        if cols_resolucion:
            col = cols_resolucion[0]
            print(f"\nColumna encontrada: '{col}'")
            print(f"Total leads: {len(df):,}\n")
            
            valores = df[col].value_counts()
            
            print(f"TOP 40 VALORES DE RESOLUCION:")
            print("-" * 80)
            for val, count in valores.head(40).items():
                pct = (count / len(df)) * 100
                print(f"{str(val):60s} | {count:6,} ({pct:5.2f}%)")
            
            # Guardar para análisis cruzado
            todos_valores[nombre] = valores.to_dict()
            
            # Buscar potenciales matriculados
            print(f"\nPOTENCIALES MATRICULADOS (contienen matricul/inscript/admitido/pago):")
            print("-" * 80)
            keywords = ['matricul', 'inscript', 'admitido', 'pago', 'aceptado', 'ingres', 'aprobad']
            for val, count in valores.items():
                val_lower = str(val).lower()
                if any(kw in val_lower for kw in keywords):
                    pct = (count / len(df)) * 100
                    print(f"  ✓ {str(val):55s} | {count:6,} ({pct:5.2f}%)")

print(f"\n{'='*100}")
print("ANALISIS COMPLETADO")
print(f"{'='*100}")
