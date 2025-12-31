"""
Analizar resoluciones únicas en UEES para entender el problema de target
"""

import pandas as pd

file_path = r'C:\Users\franc\OneDrive\Escritorio\Mis Cosas\Prob Leads - Data Science Nods\data\Consulta_Base_Unificada_UEES.xls'

print("=" * 80)
print("ANÁLISIS DE RESOLUCIONES UEES")
print("=" * 80)

# Cargar datos
df = pd.read_excel(file_path)
print(f"\nTotal leads: {len(df):,}")

# Analizar columna Resolución
if 'Resolucion' in df.columns:
    resol_col = 'Resolucion'
elif 'Resolución' in df.columns:
    resol_col = 'Resolución'
else:
    print("\n❌ No se encontró columna de resolución")
    print(f"Columnas disponibles: {df.columns.tolist()}")
    exit(1)

print(f"\nColumna encontrada: '{resol_col}'")
print(f"\n{'Resolución':<40} {'Cantidad':<10} {'%'}")
print("-" * 60)

resoluciones = df[resol_col].value_counts()
for resolucion, count in resoluciones.items():
    porcentaje = (count / len(df)) * 100
    print(f"{str(resolucion):<40} {count:<10,} {porcentaje:>6.2f}%")

print("\n" + "=" * 80)
print("VERIFICACION DE RESOLUCIONES POSITIVAS")
print("=" * 80)

resoluciones_positivas_actuales = ['Matriculado', 'Admitido', 'En proceso de pago']
print(f"\nResoluciones positivas configuradas en app.py:")
for r in resoluciones_positivas_actuales:
    print(f"  - '{r}'")

print(f"\nConteo con configuracion actual:")
matches = df[resol_col].isin(resoluciones_positivas_actuales).sum()
print(f"  Total matches: {matches} ({matches/len(df)*100:.2f}%)")

print(f"\nBuscar variaciones de 'Matriculado':")
matriculado_variations = df[resol_col].astype(str).str.contains('Matricul', case=False, na=False).sum()
print(f"  Leads con alguna variacion: {matriculado_variations}")

print(f"\nBuscar variaciones de 'Admitido':")
admitido_variations = df[resol_col].astype(str).str.contains('Admit', case=False, na=False).sum()
print(f"  Leads con alguna variacion: {admitido_variations}")

print(f"\nBuscar variaciones de 'proceso de pago':")
pago_variations = df[resol_col].astype(str).str.contains('pago|pagado', case=False, na=False).sum()
print(f"  Leads con alguna variacion: {pago_variations}")

print("\n" + "=" * 80)
