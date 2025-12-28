"""
Script de Validación de Normalización
Verifica que los datos normalizados sean consistentes entre universidades
"""

import pandas as pd
import numpy as np
from pathlib import Path
import json
import sys
import io
from collections import defaultdict

# Configurar encoding UTF-8
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def validar_esquema(df, nombre_universidad):
    """Valida que el esquema del dataframe sea consistente"""
    print(f"\n{'='*80}")
    print(f"VALIDACIÓN DE ESQUEMA: {nombre_universidad}")
    print(f"{'='*80}")
    
    # Cargar configuración
    BASE_DIR = Path(__file__).parent.parent
    CONFIG_PATH = BASE_DIR / "config" / "normalization_config.json"
    
    with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
        config = json.load(f)
    
    resultados = {
        'universidad': nombre_universidad,
        'total_leads': len(df),
        'columnas_presentes': list(df.columns),
        'errores': [],
        'advertencias': []
    }
    
    # 1. Verificar columnas requeridas
    print("\n✓ Verificando columnas requeridas...")
    columnas_requeridas = config['required_columns']
    for col in columnas_requeridas:
        if col not in df.columns:
            error = f"Columna requerida faltante: {col}"
            resultados['errores'].append(error)
            print(f"   ❌ {error}")
        else:
            print(f"   ✅ {col}")
    
    # 2. Verificar que no haya columnas de leakage
    print("\n✓ Verificando ausencia de columnas de leakage...")
    columnas_leakage = config['leakage_columns']
    for col in columnas_leakage:
        if col in df.columns:
            advertencia = f"Columna de leakage presente: {col}"
            resultados['advertencias'].append(advertencia)
            print(f"   ⚠️  {advertencia}")
    
    # 3. Verificar tipos de datos
    print("\n✓ Verificando tipos de datos...")
    tipos_esperados = config['data_types']
    for col, tipo_esperado in tipos_esperados.items():
        if col in df.columns:
            tipo_actual = str(df[col].dtype)
            if tipo_actual != tipo_esperado:
                advertencia = f"{col}: esperado {tipo_esperado}, actual {tipo_actual}"
                resultados['advertencias'].append(advertencia)
                print(f"   ⚠️  {advertencia}")
            else:
                print(f"   ✅ {col}: {tipo_actual}")
    
    # 4. Verificar columna target
    print("\n✓ Verificando columna target...")
    if 'target' in df.columns:
        valores_unicos = df['target'].unique()
        if set(valores_unicos).issubset({0, 1, np.nan}):
            print(f"   ✅ Target binario válido: {valores_unicos}")
        else:
            error = f"Target tiene valores inválidos: {valores_unicos}"
            resultados['errores'].append(error)
            print(f"   ❌ {error}")
        
        # Estadísticas de target
        positivos = df['target'].sum()
        tasa = (positivos / len(df)) * 100 if len(df) > 0 else 0
        print(f"   📊 Positivos: {positivos:,} / {len(df):,} ({tasa:.2f}%)")
    else:
        error = "Columna 'target' no encontrada"
        resultados['errores'].append(error)
        print(f"   ❌ {error}")
    
    return resultados

def validar_resoluciones(df, nombre_universidad):
    """Valida la normalización de resoluciones"""
    print(f"\n{'='*80}")
    print(f"VALIDACIÓN DE RESOLUCIONES: {nombre_universidad}")
    print(f"{'='*80}")
    
    if 'Resolución' not in df.columns:
        print("   ⚠️  Columna 'Resolución' no encontrada")
        return None
    
    # Cargar configuración
    BASE_DIR = Path(__file__).parent.parent
    CONFIG_PATH = BASE_DIR / "config" / "normalization_config.json"
    
    with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
        config = json.load(f)
    
    # Verificar categorización
    if 'resolucion_categoria' in df.columns:
        print("\n✓ Distribución de categorías:")
        categorias = df['resolucion_categoria'].value_counts()
        for cat, count in categorias.items():
            pct = (count / len(df)) * 100
            print(f"   - {cat:35s}: {count:6,} ({pct:5.2f}%)")
        
        # Verificar valores unknown
        unknown_count = (df['resolucion_categoria'] == 'unknown').sum()
        if unknown_count > 0:
            print(f"\n⚠️  {unknown_count} resoluciones no categorizadas:")
            unknown_vals = df[df['resolucion_categoria'] == 'unknown']['Resolución'].value_counts().head(10)
            for val, count in unknown_vals.items():
                print(f"      - {val}: {count}")
            return {'universidad': nombre_universidad, 'unknown_count': unknown_count}
        else:
            print("\n✅ Todas las resoluciones están categorizadas")
            return {'universidad': nombre_universidad, 'unknown_count': 0}
    else:
        print("   ❌ Columna 'resolucion_categoria' no encontrada")
        return None

def comparar_esquemas(resultados_universidades):
    """Compara esquemas entre universidades"""
    print(f"\n{'='*80}")
    print("COMPARACIÓN DE ESQUEMAS ENTRE UNIVERSIDADES")
    print(f"{'='*80}")
    
    # Obtener todas las columnas únicas
    todas_columnas = set()
    for res in resultados_universidades:
        todas_columnas.update(res['columnas_presentes'])
    
    print(f"\nTotal de columnas únicas: {len(todas_columnas)}")
    
    # Columnas comunes a todas
    columnas_comunes = set(resultados_universidades[0]['columnas_presentes'])
    for res in resultados_universidades[1:]:
        columnas_comunes &= set(res['columnas_presentes'])
    
    print(f"\n✓ Columnas comunes a todas las universidades ({len(columnas_comunes)}):")
    for col in sorted(columnas_comunes):
        print(f"   - {col}")
    
    # Columnas específicas por universidad
    print(f"\n✓ Columnas específicas por universidad:")
    for res in resultados_universidades:
        cols_unicas = set(res['columnas_presentes']) - columnas_comunes
        if cols_unicas:
            print(f"\n   {res['universidad']} ({len(cols_unicas)} únicas):")
            for col in sorted(cols_unicas):
                print(f"      - {col}")
    
    # Verificar consistencia
    print(f"\n{'='*80}")
    print("RESUMEN DE CONSISTENCIA")
    print(f"{'='*80}")
    
    total_errores = sum(len(res['errores']) for res in resultados_universidades)
    total_advertencias = sum(len(res['advertencias']) for res in resultados_universidades)
    
    print(f"\n📊 Estadísticas:")
    print(f"   - Universidades validadas: {len(resultados_universidades)}")
    print(f"   - Total errores: {total_errores}")
    print(f"   - Total advertencias: {total_advertencias}")
    
    if total_errores == 0:
        print("\n✅ VALIDACIÓN EXITOSA: No se encontraron errores")
    else:
        print(f"\n❌ VALIDACIÓN FALLIDA: {total_errores} errores encontrados")
        for res in resultados_universidades:
            if res['errores']:
                print(f"\n   {res['universidad']}:")
                for error in res['errores']:
                    print(f"      - {error}")
    
    return total_errores == 0

def validar_calidad_datos(df, nombre_universidad):
    """Valida la calidad de los datos"""
    print(f"\n{'='*80}")
    print(f"VALIDACIÓN DE CALIDAD DE DATOS: {nombre_universidad}")
    print(f"{'='*80}")
    
    # 1. Verificar duplicados
    if 'dcontacto' in df.columns:
        duplicados = df['dcontacto'].duplicated().sum()
        print(f"\n✓ Duplicados por dcontacto: {duplicados}")
        if duplicados > 0:
            print(f"   ⚠️  Se encontraron {duplicados} registros duplicados")
    
    # 2. Verificar valores nulos en columnas críticas
    print(f"\n✓ Valores nulos en columnas críticas:")
    columnas_criticas = ['dcontacto', 'Resolución', 'target', 'universidad']
    for col in columnas_criticas:
        if col in df.columns:
            nulos = df[col].isnull().sum()
            pct = (nulos / len(df)) * 100
            print(f"   - {col:20s}: {nulos:6,} ({pct:5.2f}%)")
    
    # 3. Verificar emails
    if 'tiene_email' in df.columns:
        con_email = df['tiene_email'].sum()
        pct = (con_email / len(df)) * 100
        print(f"\n✓ Leads con email válido: {con_email:,} ({pct:.2f}%)")
    
    # 4. Verificar actividad
    if 'CONTADOR_LLAMADOS_TEL' in df.columns:
        sin_llamadas = (df['CONTADOR_LLAMADOS_TEL'] == 0).sum()
        pct = (sin_llamadas / len(df)) * 100
        print(f"\n✓ Leads sin llamadas: {sin_llamadas:,} ({pct:.2f}%)")

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Validar normalización de datos')
    parser.add_argument('--check-resolutions', action='store_true', 
                        help='Verificar normalización de resoluciones')
    parser.add_argument('--check-quality', action='store_true',
                        help='Verificar calidad de datos')
    args = parser.parse_args()
    
    BASE_DIR = Path(__file__).parent.parent
    DATA_DIR = BASE_DIR / "data"
    
    print("="*80)
    print("VALIDADOR DE NORMALIZACIÓN MULTI-UNIVERSIDAD")
    print("="*80)
    
    # Cargar datos normalizados
    archivo_normalizado = DATA_DIR / "datos_multi_universidad_limpios.csv"
    
    if not archivo_normalizado.exists():
        print(f"\n❌ Error: No se encontró {archivo_normalizado}")
        print("   Ejecuta primero: python scripts/prepare_multi_university_data.py")
        sys.exit(1)
    
    print(f"\n📂 Cargando datos normalizados...")
    df_completo = pd.read_csv(archivo_normalizado)
    print(f"✅ Cargados {len(df_completo):,} leads")
    
    # Validar por universidad
    resultados = []
    universidades = df_completo['universidad'].unique()
    
    for uni in universidades:
        df_uni = df_completo[df_completo['universidad'] == uni]
        
        # Validación de esquema
        res = validar_esquema(df_uni, uni)
        resultados.append(res)
        
        # Validación de resoluciones (opcional)
        if args.check_resolutions:
            validar_resoluciones(df_uni, uni)
        
        # Validación de calidad (opcional)
        if args.check_quality:
            validar_calidad_datos(df_uni, uni)
    
    # Comparar esquemas
    exito = comparar_esquemas(resultados)
    
    # Código de salida
    sys.exit(0 if exito else 1)
