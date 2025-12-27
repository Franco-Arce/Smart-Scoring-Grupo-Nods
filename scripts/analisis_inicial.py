import pandas as pd
import numpy as np
import sys
import io

# Configurar encoding UTF-8
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Cargar datos
df = pd.read_excel('Consulta_Base_Unificada_UNAB.xls')

print("="*80)
print("ANALISIS INICIAL DE DATOS - SMART SCORING UNAB")
print("="*80)

print(f"\nTotal de leads: {len(df)}")
print(f"Columnas disponibles: {len(df.columns)}")

print("\n" + "="*80)
print("1. ANÁLISIS DE LA VARIABLE OBJETIVO (MATRÍCULA)")
print("="*80)

# Analizar resoluciones para identificar matrículas
print("\nUltimas Resoluciones (Top 20):")
print(df['Ultima resolución'].value_counts().head(20))

print("\nResoluciones (Top 20):")
print(df['Resolución'].value_counts().head(20))

print("\nEstado Principal:")
print(df['Estado principal'].value_counts())

print("\n" + "="*80)
print("2. CALIDAD DE DATOS")
print("="*80)

# Revisar valores nulos
print("\nValores nulos por columna:")
nulos = df.isnull().sum()
nulos_pct = (nulos / len(df)) * 100
df_nulos = pd.DataFrame({
    'Columna': nulos.index,
    'Nulos': nulos.values,
    'Porcentaje': nulos_pct.values
}).sort_values('Nulos', ascending=False)
print(df_nulos[df_nulos['Nulos'] > 0].to_string(index=False))

print("\n" + "="*80)
print("3. ANÁLISIS DE COMPORTAMIENTO DEL LEAD")
print("="*80)

print("\nEstadisticas de Llamadas:")
print(df['CONTADOR_LLAMADOS_TEL'].describe())

print("\nLlamadas del Discador:")
print(df['Llamadas_discador'].describe())

print("\nWhatsApp Entrante:")
print(f"Leads con WhatsApp entrante: {df['WhatsApp entrante'].notna().sum()} ({(df['WhatsApp entrante'].notna().sum()/len(df)*100):.1f}%)")

print("\n" + "="*80)
print("4. ANÁLISIS DE FUENTES DE MARKETING")
print("="*80)

print("\nUTM Medium:")
print(df['UTM Medium'].value_counts().head(10))

print("\nUTM Source:")
print(df['UTM Source'].value_counts().head(10))

print("\nBase de Datos:")
print(df['Base de datos'].value_counts())

print("\n" + "="*80)
print("5. ANÁLISIS DE PROGRAMAS")
print("="*80)

print("\nTop 15 Programas de Interes:")
print(df['Programa interes'].value_counts().head(15))

print("\n" + "="*80)
print("6. ANÁLISIS TEMPORAL")
print("="*80)

# Crear columnas de fecha
df['Fecha insert Lead'] = pd.to_datetime(df['Fecha insert Lead'], errors='coerce')
df['Fecha y hora de actualización'] = pd.to_datetime(df['Fecha y hora de actualización'], errors='coerce')

print("\nRango de fechas de insercion:")
print(f"Desde: {df['Fecha insert Lead'].min()}")
print(f"Hasta: {df['Fecha insert Lead'].max()}")

# Calcular tiempo de gestion
df['dias_gestion'] = (df['Fecha y hora de actualización'] - df['Fecha insert Lead']).dt.days

print("\nTiempo de Gestion (dias):")
print(df['dias_gestion'].describe())

print("\n" + "="*80)
print("7. DETECCIÓN DE PROBLEMAS DE CALIDAD")
print("="*80)

# Telefonos
print(f"\nTelefonos unicos: {df['TELTELEFONO'].nunique()}")
print(f"Leads con telefono duplicado: {df['TELTELEFONO'].duplicated().sum()}")

# Emails
print(f"\nEmails unicos: {df['EMLMAIL'].nunique()}")
print(f"Leads sin email: {df['EMLMAIL'].isna().sum()}")

# Nombres
print(f"\nLeads sin nombre: {df['Nombre y Apellido'].isna().sum()}")

print("\n" + "="*80)
print("ANÁLISIS COMPLETADO")
print("="*80)
