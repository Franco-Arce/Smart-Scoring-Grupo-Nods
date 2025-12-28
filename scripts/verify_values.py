import pandas as pd

df = pd.read_csv('data/datos_multi_universidad_limpios.csv', low_memory=False)

print('='*80)
print('VERIFICACIÓN DE NORMALIZACIÓN DE VALORES')
print('='*80)

print('\n=== Canal (después de normalización) ===')
print(df['Canal'].value_counts().head(15))

print('\n=== Verificando whatsapp unificado ===')
print(f'Total whatsapp: {(df["Canal"] == "whatsapp").sum()}')
print(f'Total registros: {len(df)}')

print('\n=== Programa interes (muestra) ===')
print(df['Programa interes'].value_counts().head(10))

print('\n=== UTM Source (después de normalización) ===')
print(df['UTM Source'].value_counts().head(10))
