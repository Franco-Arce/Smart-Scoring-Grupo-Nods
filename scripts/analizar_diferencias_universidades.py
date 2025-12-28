"""
Análisis de Diferencias Entre Universidades
Analiza columnas, formatos y distribuciones para tomar decisiones de features
"""

import pandas as pd
import numpy as np
from pathlib import Path
import json

def analizar_universidad(archivo_path, nombre):
    """Analiza en detalle un archivo de universidad"""
    print(f"\n{'='*80}")
    print(f"ANÁLISIS: {nombre}")
    print(f"{'='*80}")
    
    df = pd.read_excel(archivo_path)
    
    print(f"\nINFORMACION BASICA:")
    print(f"   Total leads: {len(df):,}")
    print(f"   Total columnas: {len(df.columns)}")
    
    # Analizar columnas
    print(f"\nCOLUMNAS PRESENTES:")
    for col in sorted(df.columns):
        non_null = df[col].notna().sum()
        pct_filled = (non_null / len(df)) * 100
        dtype = str(df[col].dtype)
        print(f"   - {col:40s} | {dtype:10s} | {pct_filled:5.1f}% lleno")
    
    # Analizar Resolución (target)
    if 'Resolución' in df.columns or 'Resolucion' in df.columns:
        col_res = 'Resolución' if 'Resolución' in df.columns else 'Resolucion'
        print(f"\nDISTRIBUCION DE RESOLUCION:")
        valores = df[col_res].value_counts()
        total = len(df)
        for val, count in valores.head(10).items():
            pct = (count / total) * 100
            print(f"   {str(val):40s}: {count:6,} ({pct:5.2f}%)")
        
        # Detectar matriculados
        matriculados = df[col_res].apply(
            lambda x: 1 if str(x).strip() in ['Matriculado', 'Admitido', 'En proceso de pago'] else 0
        ).sum()
        tasa = (matriculados / total) * 100
        print(f"\n   LEADS MATRICULADOS: {matriculados:,} ({tasa:.2f}%)")
    
    # Analizar UTMs
    print(f"\nANALISIS DE UTMs:")
    for utm_col in ['UTM Source', 'UTM Medium', 'UTM Campaing']:
        if utm_col in df.columns:
            valores = df[utm_col].value_counts()
            print(f"\n   {utm_col}:")
            for val, count in valores.head(5).items():
                print(f"      - {str(val):30s}: {count:6,}")
    
    # Analizar llamadas
    print(f"\nANALISIS DE ACTIVIDAD:")
    for call_col in ['CONTADOR_LLAMADOS_TEL', 'Contador de Llamadas', 'Llamadas_discador', 'Lamadas_discador']:
        if call_col in df.columns:
            vals = df[call_col].dropna()
            if len(vals) > 0:
                print(f"   {call_col}:")
                print(f"      - Mean: {vals.mean():.2f}")
                print(f"      - Median: {vals.median():.2f}")
                print(f"      - Max: {vals.max():.0f}")
    
    # Analizar WhatsApp
    print(f"\nANALISIS DE WHATSAPP:")
    for ws_col in ['WhatsApp entrante', 'CHKENTRANTEWHATSAPP']:
        if ws_col in df.columns:
            valores = df[ws_col].value_counts()
            print(f"   {ws_col}:")
            for val, count in valores.head(5).items():
                print(f"      - {str(val):20s}: {count:6,}")
    
    return {
        'nombre': nombre,
        'total_leads': len(df),
        'columnas': list(df.columns),
        'tasa_matriculacion': tasa if 'Resolución' in df.columns or 'Resolucion' in df.columns else 0
    }

def comparar_columnas(resultados):
    """Compara columnas entre universidades"""
    print(f"\n{'=>'*80}")
    print(f"COMPARACION DE COLUMNAS ENTRE UNIVERSIDADES")
    print(f"{'=>'*80}")
    
    # Obtener todas las columnas únicas
    todas_columnas = set()
    for res in resultados:
        todas_columnas.update(res['columnas'])
    
    print(f"\nTOTAL COLUMNAS UNICAS: {len(todas_columnas)}\n")
    
    # Crear matriz de presencia
    print("MATRIZ DE PRESENCIA DE COLUMNAS:\n")
    
    # Columnas comunes a todas
    columnas_comunes = set(resultados[0]['columnas'])
    for res in resultados[1:]:
        columnas_comunes &= set(res['columnas'])
    
    print(f"COLUMNAS COMUNES A TODAS ({len(columnas_comunes)}):") 
    for col in sorted(columnas_comunes):
        print(f"   - {col}")
    
    # Columnas específicas por universidad
    print(f"\nCOLUMNAS ESPECIFICAS POR UNIVERSIDAD:")
    for res in resultados:
        cols_unicas = set(res['columnas']) - columnas_comunes
        if cols_unicas:
            print(f"\n   {res['nombre']} ({len(cols_unicas)} unicas):")
            for col in sorted(cols_unicas):
                print(f"      - {col}")

def identificar_columnas_leakage():
    """Identifica qué columnas tienen data leakage"""
    print(f"\n{'='*80}")
    print("CLASIFICACION DE COLUMNAS")
    print(f"{'='*80}")
    
    print("\nCOLUMNAS CON DATA LEAKAGE (NO USAR):")
    leakage = [
        'Resolución',
        'Resolucion',
        'Ultima resolución',
        'Ultima resolucion',
        'Estado principal',  # Puede contener "Matriculado"
    ]
    for col in leakage:
        print(f"   - {col:40s} (informacion del futuro)")
    
    print("\nCOLUMNAS VALIDAS PARA FEATURES:")
    validas = [
        'universidad',  # NUEVO - muy importante
        'CONTADOR_LLAMADOS_TEL',
        'Contador de Llamadas',
        'Llamadas_discador',
        'Lamadas_discador',
        'dias_gestion',
        'ratio_llamadas_dias',
        'programa_categoria',
        'base_categoria',
        'Base de datos',
        'utm_source_clean',
        'utm_medium_clean',
        'UTM Source',
        'UTM Medium',
        'UTM Campaing',
        'UTM Content',
        'tiene_email',
        'whatsapp_entrante_flag',
        'WhatsApp entrante',
        'CHKENTRANTEWHATSAPP',
        'WhatsApp',  # Campo de contacto
        'TELWHATSAPP',
        'lead_reciente',
        'lead_antiguo',
        'alta_actividad_llamadas',
        'Programa interes',
        'Fecha insert Lead',
        'Fecha y hora de actualización',
        'Canal',
        'Operador',
        'Nombre Operador',
    ]
    for col in sorted(validas):
        print(f"   - {col}")
    
    print("\nCOLUMNAS A EVALUAR (pueden tener leakage parcial):")
    evaluar = [
        'Fecha y hora del próximo llamado',  # Puede indicar abandono
        'Mensaje',  # Puede contener info del resultado
    ]
    for col in evaluar:
        print(f"   - {col}")

if __name__ == "__main__":
    BASE_DIR = Path(__file__).parent.parent
    DATA_DIR = BASE_DIR / "data"
    
    # Archivos de universidades
    archivos = {
        'UNAB': DATA_DIR / 'Consulta_Base_Unificada_UNAB.xls',
        'Crexe': DATA_DIR / 'Reporte_Bases_Unificadas_Crexe.xls',
        'UEES': DATA_DIR / 'Consulta_Base_Unificada_UEES.xls',
        'Anahuac': DATA_DIR / 'Consulta_Base_Unificada_Anahuac.xls',
        'Unisangil': DATA_DIR / 'Consulta_Base_Unificada_Unisangil.xls'
    }
    
    # Analizar cada universidad
    resultados = []
    for nombre, archivo in archivos.items():
        if archivo.exists():
            res = analizar_universidad(archivo, nombre)
            resultados.append(res)
    
    # Comparar columnas
    comparar_columnas(resultados)
    
    # Identificar leakage
    identificar_columnas_leakage()
    
    # Resumen final
    print(f"\n{'='*80}")
    print("RESUMEN DE TASAS DE MATRICULACIÓN")
    print(f"{'='*80}\n")
    
    for res in resultados:
        print(f"   {res['nombre']:12s}: {res['total_leads']:6,} leads → {res['tasa_matriculacion']:5.2f}% matriculados")
    
    print(f"\n{'='*80}")
    print("ANÁLISIS COMPLETADO")
    print(f"{'='*80}")
