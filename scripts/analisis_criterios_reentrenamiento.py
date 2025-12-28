"""
Análisis Simplificado de Datos Multi-Universidad
Genera reporte detallado sin problemas de encoding
"""

import pandas as pd
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent
df = pd.read_csv(BASE_DIR / "data" / "datos_multi_universidad_features.csv", low_memory=False)

print("="*80)
print("ANALISIS DE DATOS MULTI-UNIVERSIDAD")
print("="*80)

print(f"\nTOTAL LEADS: {len(df):,}")
print(f"TOTAL COLUMNAS: {len(df.columns)}")

# Análisis por universidad
print("\n" + "="*80)
print("DISTRIBUCION POR UNIVERSIDAD")
print("="*80 + "\n")

for uni in sorted(df['universidad'].unique()):
    df_uni = df[df['universidad'] == uni]
    positivos = df_uni['target'].sum()
    tasa = (positivos / len(df_uni)) * 100
    print(f"{uni:12s}: {len(df_uni):6,} leads | {positivos:4.0f} matriculados | {tasa:5.2f}%")

# Columnas del dataset
print("\n" + "="*80)
print("COLUMNAS DISPONIBLES EN EL DATASET")
print("="*80 + "\n")

for i, col in enumerate(sorted(df.columns), 1):
    print(f"{i:3d}. {col}")

# Identificar columnas problemáticas
print("\n" + "="*80)
print("COLUMNAS CON DATA LEAKAGE - NO USAR")
print("="*80 + "\n")

leakage_cols = [
    'Resolución',
    'Resolucion', 
    'Ultima resolución',
    'Ultima resolucion',
    'Estado principal',
]

for col in leakage_cols:
    if col in df.columns:
        print(f"  X {col:40s} (informacion del futuro)")

print("\n" + "="*80)
print("COLUMNAS VALIDAS PARA MODELO SIN LEAKAGE")
print("="*80 + "\n")

valid_cols = [
    'universidad',
    'CONTADOR_LLAMADOS_TEL',
    'Llamadas_discador',
    'dias_gestion',
    'ratio_llamadas_dias',
    'programa_categoria',
    'base_categoria',
    'utm_source_clean',
    'utm_medium_clean',
    'tiene_email',
    'whatsapp_entrante_flag',
    'lead_reciente',
    'lead_antiguo',
    'alta_actividad_llamadas',
    'Base de datos',
    'WhatsApp',
    'TELWHATSAPP',
    'UTM Source',
    'UTM Medium',
    'UTM Campaing',
    'Canal',
]

print("FEATURES QUE USAREMOS:\n")
features_disponibles = [col for col in valid_cols if col in df.columns]
for i, col in enumerate(features_disponibles, 1):
    non_null = df[col].notna().sum()
    pct = (non_null / len(df)) * 100
    print(f"{i:2d}. {col:35s} | {pct:5.1f}% disponible")

print(f"\nTOTAL FEATURES VALIDAS: {len(features_disponibles)}")

# Estadísticas de features importantes
print("\n" + "="*80)
print("ESTADISTICAS DE FEATURES CLAVE")
print("="*80 + "\n")

print("ACTIVIDAD DE LLAMADAS:")
if 'CONTADOR_LLAMADOS_TEL' in df.columns:
    vals = df['CONTADOR_LLAMADOS_TEL'].dropna()
    print(f"  Media: {vals.mean():.2f} llamadas")
    print(f"  Mediana: {vals.median():.0f} llamadas")
    print(f"  Max: {vals.max():.0f} llamadas")

print("\nDIAS DE GESTION:")
if 'dias_gestion' in df.columns:
    vals = df['dias_gestion'].dropna()
    print(f"  Media: {vals.mean():.1f} dias")
    print(f"  Mediana: {vals.median():.0f} dias")
    print(f"  Max: {vals.max():.0f} dias")

print("\nRATIO LLAMADAS/DIAS:")
if 'ratio_llamadas_dias' in df.columns:
    vals = df['ratio_llamadas_dias'].dropna()
    print(f"  Media: {vals.mean():.3f}")
    print(f"  Mediana: {vals.median():.3f}")

print("\n" + "="*80)
print("CRITERIOS PARA REENTRENAMIENTO")
print("="*80 + "\n")

print("1. OBJETIVO:")
print("   Predecir probabilidad de matricula ANTES de conocer el  resultado")
print("   usando solo informacion disponible al momento de contacto inicial\n")

print("2. FEATURES A USAR:")
print(f"   - Total: {len(features_disponibles)} features validas")
print("   - Incluye: universidad (CRITICO para diferenciar instituciones)")
print("   - Incluye: Comportamiento (llamadas, whatsapp, dias de gestion)")
print("   - Incluye: Origen (UTMs, canal)")
print("   - Incluye: Programa/Base de datos\n")

print("3. FEATURES EXCLUIDAS:")
print("   - Resolucion (target derivado de esta columna)")
print("   - Ultima resolucion (outcome pasado)")
print("   - Estado principal (puede contener informacion del futuro)\n")

print("4. TARGET:")
print("   - Variable: 'target' (1 = Matriculado, 0 = No matriculado)")
print(f"   - Positivos globales: {df['target'].sum():,} ({df['target'].mean()*100:.2f}%)")
print("   - Desbalanceado: usaremos class_weight='balanced'\n")

print("5. METRICAS ESPERADAS:")
print("   - AUC-ROC: 0.85 - 0.92 (realista vs 0.9992 fake)")
print("   - Accuracy: 90-95%")
print("   - Recall: 70-85% (capturar mayoria de matriculados)")
print("   - Precision: 25-40% (acceptable para call center)\n")

print("6. VALIDACION:")
print("   - Split: 80% train / 20% test")
print("   - Stratified by: universidad + target")
print("   - Metricas por universidad para validar consistencia")

print("\n" + "="*80)
print("ANALISIS COMPLETADO - LISTO PARA REENTRENAR")
print("="*80)
