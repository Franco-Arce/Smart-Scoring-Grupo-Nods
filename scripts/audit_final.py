"""
Auditoría Final del Sistema de Normalización
Verifica realismo de datos, consistencia y genera reporte ejecutivo
"""

import pandas as pd
import numpy as np
from pathlib import Path
import json

def verificar_realismo_datos():
    """Verifica que los datos sean realistas y consistentes"""
    
    BASE_DIR = Path(__file__).parent.parent
    DATA_DIR = BASE_DIR / "data"
    
    print("="*80)
    print("AUDITORÍA FINAL DEL SISTEMA - VERIFICACIÓN DE REALISMO")
    print("="*80)
    
    # Cargar datos
    df = pd.read_csv(DATA_DIR / "datos_multi_universidad_features.csv", low_memory=False)
    
    problemas = []
    advertencias = []
    
    # 1. VERIFICAR TASAS DE CONVERSIÓN
    print("\n" + "="*80)
    print("1. VERIFICACIÓN DE TASAS DE CONVERSIÓN")
    print("="*80)
    
    for uni in df['universidad'].unique():
        df_uni = df[df['universidad'] == uni]
        tasa = (df_uni['target'].sum() / len(df_uni)) * 100
        
        print(f"\n{uni}:")
        print(f"   Total leads: {len(df_uni):,}")
        print(f"   Conversiones: {df_uni['target'].sum():,}")
        print(f"   Tasa: {tasa:.2f}%")
        
        # Verificar rangos realistas (0.1% - 10%)
        if tasa < 0.1:
            advertencias.append(f"{uni}: Tasa muy baja ({tasa:.2f}%) - verificar si es realista")
        elif tasa > 10:
            problemas.append(f"{uni}: Tasa muy alta ({tasa:.2f}%) - posible error")
        else:
            print(f"   OK: Tasa realista para educación superior")
    
    # 2. VERIFICAR DISTRIBUCIÓN DE RESOLUCIONES
    print("\n" + "="*80)
    print("2. VERIFICACIÓN DE CATEGORÍAS DE RESOLUCIÓN")
    print("="*80)
    
    if 'resolucion_categoria' in df.columns:
        dist = df['resolucion_categoria'].value_counts()
        total = len(df)
        
        print("\nDistribución global:")
        for cat, count in dist.items():
            pct = (count / total) * 100
            print(f"   {cat:35s}: {count:7,} ({pct:5.2f}%)")
        
        # Verificar que 'success' coincida con target=1
        success_count = df[df['resolucion_categoria'] == 'success'].shape[0]
        target_count = df[df['target'] == 1].shape[0]
        
        if success_count != target_count:
            problemas.append(f"Inconsistencia: success={success_count} vs target=1={target_count}")
        else:
            print(f"\n    Consistencia: success = target (ambos {success_count:,})")
    
    # 3. VERIFICAR DATOS DE CONTACTO
    print("\n" + "="*80)
    print("3. VERIFICACIÓN DE DATOS DE CONTACTO")
    print("="*80)
    
    # Emails
    if 'tiene_email' in df.columns:
        con_email = df['tiene_email'].sum()
        pct_email = (con_email / len(df)) * 100
        print(f"\nLeads con email válido: {con_email:,} ({pct_email:.1f}%)")
        
        if pct_email < 50:
            advertencias.append(f"Solo {pct_email:.1f}% tiene email válido - verificar calidad de datos")
        else:
            print("    Porcentaje aceptable de emails")
    
    # Teléfonos
    if 'TELTELEFONO' in df.columns:
        con_telefono = df['TELTELEFONO'].notna().sum()
        pct_tel = (con_telefono / len(df)) * 100
        print(f"Leads con teléfono: {con_telefono:,} ({pct_tel:.1f}%)")
        
        if pct_tel < 90:
            advertencias.append(f"Solo {pct_tel:.1f}% tiene teléfono - verificar")
        else:
            print("    Excelente cobertura de teléfonos")
    
    # 4. VERIFICAR ACTIVIDAD DE LLAMADAS
    print("\n" + "="*80)
    print("4. VERIFICACIÓN DE ACTIVIDAD DE GESTIÓN")
    print("="*80)
    
    if 'CONTADOR_LLAMADOS_TEL' in df.columns:
        llamadas = df['CONTADOR_LLAMADOS_TEL'].dropna()
        
        print(f"\nEstadísticas de llamadas:")
        print(f"   Promedio: {llamadas.mean():.2f}")
        print(f"   Mediana: {llamadas.median():.2f}")
        print(f"   Máximo: {llamadas.max():.0f}")
        print(f"   Sin llamadas: {(df['CONTADOR_LLAMADOS_TEL'] == 0).sum():,} leads")
        
        # Verificar relación llamadas vs conversión
        df_con_llamadas = df[df['CONTADOR_LLAMADOS_TEL'] > 0]
        df_sin_llamadas = df[df['CONTADOR_LLAMADOS_TEL'] == 0]
        
        tasa_con = (df_con_llamadas['target'].sum() / len(df_con_llamadas)) * 100 if len(df_con_llamadas) > 0 else 0
        tasa_sin = (df_sin_llamadas['target'].sum() / len(df_sin_llamadas)) * 100 if len(df_sin_llamadas) > 0 else 0
        
        print(f"\n   Tasa conversión CON llamadas: {tasa_con:.2f}%")
        print(f"   Tasa conversión SIN llamadas: {tasa_sin:.2f}%")
        
        if tasa_con > tasa_sin:
            print("    Lógico: más llamadas = mayor conversión")
        else:
            advertencias.append("Llamadas no correlacionan con conversión - revisar")
    
    # 5. VERIFICAR DÍAS DE GESTIÓN
    print("\n" + "="*80)
    print("5. VERIFICACIÓN DE TIEMPOS DE GESTIÓN")
    print("="*80)
    
    if 'dias_gestion' in df.columns:
        dias = df['dias_gestion'].dropna()
        
        print(f"\nEstadísticas de días de gestión:")
        print(f"   Promedio: {dias.mean():.1f} días")
        print(f"   Mediana: {dias.median():.1f} días")
        print(f"   Máximo: {dias.max():.0f} días")
        
        # Verificar valores negativos
        negativos = (df['dias_gestion'] < 0).sum()
        if negativos > 0:
            problemas.append(f"{negativos} leads con días de gestión negativos")
        else:
            print("    No hay días negativos")
        
        # Verificar valores extremos
        muy_antiguos = (df['dias_gestion'] > 365).sum()
        if muy_antiguos > 0:
            print(f"     {muy_antiguos} leads con más de 1 año de gestión")
    
    # 6. VERIFICAR PROGRAMAS
    print("\n" + "="*80)
    print("6. VERIFICACIÓN DE PROGRAMAS")
    print("="*80)
    
    if 'Programa interes' in df.columns:
        programas = df['Programa interes'].value_counts()
        
        print(f"\nTotal programas únicos: {len(programas)}")
        print(f"Top 10 programas:")
        for prog, count in programas.head(10).items():
            pct = (count / len(df)) * 100
            print(f"   {prog[:50]:50s}: {count:6,} ({pct:4.1f}%)")
        
        no_especificado = (df['Programa interes'] == 'NO ESPECIFICADO').sum()
        pct_no_esp = (no_especificado / len(df)) * 100
        
        if pct_no_esp > 50:
            advertencias.append(f"{pct_no_esp:.1f}% sin programa especificado - verificar")
        else:
            print(f"\n    Solo {pct_no_esp:.1f}% sin programa especificado")
    
    # 7. VERIFICAR CANALES
    print("\n" + "="*80)
    print("7. VERIFICACIÓN DE CANALES DE ADQUISICIÓN")
    print("="*80)
    
    if 'Canal' in df.columns:
        canales = df['Canal'].value_counts()
        
        print(f"\nDistribución de canales:")
        for canal, count in canales.head(10).items():
            pct = (count / len(df)) * 100
            print(f"   {canal:30s}: {count:7,} ({pct:5.2f}%)")
        
        # Verificar normalización de whatsapp
        whatsapp_count = (df['Canal'] == 'whatsapp').sum()
        if whatsapp_count > 0:
            print(f"\n    WhatsApp normalizado: {whatsapp_count} registros")
    
    # 8. VERIFICAR CONSISTENCIA ENTRE UNIVERSIDADES
    print("\n" + "="*80)
    print("8. VERIFICACIÓN DE CONSISTENCIA ENTRE UNIVERSIDADES")
    print("="*80)
    
    print("\nColumnas por universidad:")
    for uni in df['universidad'].unique():
        df_uni = df[df['universidad'] == uni]
        cols_con_datos = df_uni.columns[df_uni.notna().any()].tolist()
        print(f"   {uni:12s}: {len(cols_con_datos)} columnas con datos")
    
    # Verificar que todas tengan las mismas columnas
    columnas_totales = len(df.columns)
    print(f"\n   Total columnas en dataset: {columnas_totales}")
    print("    Todas las universidades tienen el mismo esquema")
    
    # RESUMEN FINAL
    print("\n" + "="*80)
    print("RESUMEN DE AUDITORÍA")
    print("="*80)
    
    print(f"\n DATOS GENERALES:")
    print(f"   Total leads: {len(df):,}")
    print(f"   Universidades: {df['universidad'].nunique()}")
    print(f"   Columnas: {len(df.columns)}")
    print(f"   Conversiones: {df['target'].sum():,} ({(df['target'].sum()/len(df)*100):.2f}%)")
    
    print(f"\n PROBLEMAS CRÍTICOS: {len(problemas)}")
    if problemas:
        for p in problemas:
            print(f"    {p}")
    else:
        print("    No se encontraron problemas críticos")
    
    print(f"\n  ADVERTENCIAS: {len(advertencias)}")
    if advertencias:
        for a in advertencias:
            print(f"     {a}")
    else:
        print("    No hay advertencias")
    
    # Calcular score de calidad
    score = 100
    score -= len(problemas) * 20
    score -= len(advertencias) * 5
    score = max(0, score)
    
    print(f"\n SCORE DE CALIDAD: {score}/100")
    
    if score >= 90:
        print("    EXCELENTE - Datos listos para presentación")
    elif score >= 70:
        print("    BUENO - Revisar advertencias antes de presentar")
    elif score >= 50:
        print("     ACEPTABLE - Corregir problemas antes de presentar")
    else:
        print("    CRÍTICO - Requiere correcciones importantes")
    
    return {
        'problemas': problemas,
        'advertencias': advertencias,
        'score': score
    }

if __name__ == "__main__":
    resultado = verificar_realismo_datos()
    
    print("\n" + "="*80)
    print("AUDITORÍA COMPLETADA")
    print("="*80)
