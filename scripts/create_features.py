"""
Feature Engineering - Smart Scoring UNAB
Crea variables adicionales que mejoran la prediccion del modelo
"""

import pandas as pd
import numpy as np
import sys
import io
from pathlib import Path

# Configurar encoding UTF-8
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def crear_features(df):
    """
    Crea features adicionales para el modelo de ML
    
    Args:
        df: DataFrame limpio
        
    Returns:
        DataFrame con features nuevas
    """
    print("="*80)
    print("INICIANDO FEATURE ENGINEERING - SMART SCORING")
    print("="*80)
    
    df_features = df.copy()
    
    # 1. Features de Email
    print("\n[1/8] Creando features de Email...")
    df_features['tiene_email'] = df_features['email_valido'].astype(int)
    print(f"   -> tiene_email: {df_features['tiene_email'].sum()} leads con email valido")
    
    # 2. Features de WhatsApp
    print("\n[2/8] Creando features de WhatsApp...")
    df_features['whatsapp_entrante_flag'] = (
        df_features['WhatsApp entrante'].notna()
    ).astype(int)
    print(f"   -> whatsapp_entrante_flag: {df_features['whatsapp_entrante_flag'].sum()} "
          "leads con WhatsApp entrante")
    
    # 3. Features Temporales
    print("\n[3/8] Creando features temporales...")
    
    # Lead reciente (menos de 7 dias)
    df_features['lead_reciente'] = (df_features['dias_gestion'] < 7).astype(int)
    
    # Lead antiguo (mas de 30 dias)
    df_features['lead_antiguo'] = (df_features['dias_gestion'] > 30).astype(int)
    
    print(f"   -> lead_reciente (<7 dias): {df_features['lead_reciente'].sum()}")
    print(f"   -> lead_antiguo (>30 dias): {df_features['lead_antiguo'].sum()}")
    
    # 4. Features de Comportamiento
    print("\n[4/8] Creando features de comportamiento...")
    
    # Ratio de llamadas por dia
    df_features['ratio_llamadas_dias'] = df_features.apply(
        lambda row: row['CONTADOR_LLAMADOS_TEL'] / max(row['dias_gestion'], 1),
        axis=1
    )
    
    # Alta actividad de llamadas (>5 intentos)
    df_features['alta_actividad_llamadas'] = (
        df_features['CONTADOR_LLAMADOS_TEL'] > 5
    ).astype(int)
    
    print(f"   -> ratio_llamadas_dias promedio: {df_features['ratio_llamadas_dias'].mean():.2f}")
    print(f"   -> alta_actividad_llamadas: {df_features['alta_actividad_llamadas'].sum()}")
    
    # 5. Categorizar Programas
    print("\n[5/8] Categorizando programas...")
    
    def categorizar_programa(programa):
        programa_str = str(programa).upper()
        
        if 'TECNOLOGÍA' in programa_str or 'TECNOLOGIA' in programa_str:
            return 'TECNOLOGIA'
        elif 'ESPECIALIZACIÓN' in programa_str or 'ESPECIALIZACION' in programa_str:
            return 'ESPECIALIZACION'
        elif 'MAESTRÍA' in programa_str or 'MAESTRIA' in programa_str:
            return 'MAESTRIA'
        elif 'DERECHO' in programa_str:
            return 'DERECHO'
        elif 'ADMINISTR' in programa_str or 'NEGOCIO' in programa_str or 'CONTAD' in programa_str:
            return 'NEGOCIOS'
        elif 'SALUD' in programa_str or 'FARMACIA' in programa_str or 'EPIDEMIO' in programa_str:
            return 'SALUD'
        else:
            return 'OTROS'
    
    df_features['programa_categoria'] = df_features['Programa interes'].apply(
        categorizar_programa
    )
    
    print("   -> Distribucion de categorias:")
    print(df_features['programa_categoria'].value_counts().to_string())
    
    # 6. Categorizar Base de Datos
    print("\n[6/8] Categorizando base de datos...")
    
    def categorizar_base(base):
        base_str = str(base).upper()
        
        if 'PREGRADO' in base_str:
            return 'PREGRADO'
        elif 'POSGRADO' in base_str or 'POSTGRADO' in base_str:
            return 'POSGRADO'
        elif 'LETO' in base_str:
            return 'LETO'
        else:
            return 'OTRO'
    
    df_features['base_categoria'] = df_features['Base de datos'].apply(
        categorizar_base
    )
    
    print("   -> Distribucion de bases:")
    print(df_features['base_categoria'].value_counts().to_string())
    
    # 7. Limpiar UTM Source
    print("\n[7/8] Limpiando UTM Source...")
    
    def limpiar_utm_source(source):
        source_str = str(source).lower()
        
        if 'google' in source_str:
            return 'google'
        elif 'fb' in source_str or 'facebook' in source_str:
            return 'facebook'
        else:
            return 'otros'
    
    df_features['utm_source_clean'] = df_features['UTM Source'].apply(
        limpiar_utm_source
    )
    
    print("   -> Distribucion de fuentes:")
    print(df_features['utm_source_clean'].value_counts().to_string())
    
    # 8. Limpiar UTM Medium
    print("\n[8/8] Limpiando UTM Medium...")
    
    def limpiar_utm_medium(medium):
        medium_str = str(medium).lower()
        
        if 'paid' in medium_str or 'social' in medium_str:
            return 'paid_social'
        elif 'organic' in medium_str:
            return 'organic'
        else:
            return 'otros'
    
    df_features['utm_medium_clean'] = df_features['UTM Medium'].apply(
        limpiar_utm_medium
    )
    
    print("   -> Distribucion de medios:")
    print(df_features['utm_medium_clean'].value_counts().to_string())
    
    print("\n" + "="*80)
    print("FEATURE ENGINEERING COMPLETADO")
    print("="*80)
    print(f"\nFeatures nuevas creadas: 11")
    print(f"Total de columnas ahora: {len(df_features.columns)}")
    
    return df_features

def seleccionar_columnas_modelo(df):
    """
    Selecciona solo las columnas necesarias para el modelo
    """
    print("\n" + "="*80)
    print("SELECCIONANDO COLUMNAS PARA EL MODELO")
    print("="*80)
    
    # Columnas numericas directas
    columnas_numericas = [
        'CONTADOR_LLAMADOS_TEL',
        'Llamadas_discador',
        'dias_gestion',
        'ratio_llamadas_dias'
    ]
    
    # Columnas categoricas (ya procesadas)
    columnas_categoricas = [
        'programa_categoria',
        'base_categoria',
        'utm_source_clean',
        'utm_medium_clean'
    ]
    
    # Flags binarios
    columnas_flags = [
        'tiene_email',
        'whatsapp_entrante_flag',
        'lead_reciente',
        'lead_antiguo',
        'alta_actividad_llamadas'
    ]
    
    # Target
    columnas_target = ['target']
    
    # Columnas de identificacion (para referencia, no para modelo)
    columnas_id = [
        'dcontacto',
        'Nombre y Apellido',
        'TELTELEFONO',
        'EMLMAIL',
        'Programa interes'
    ]
    
    todas_columnas = (
        columnas_id + 
        columnas_numericas + 
        columnas_categoricas + 
        columnas_flags + 
        columnas_target
    )
    
    df_modelo = df[todas_columnas].copy()
    
    print(f"\n Columnas seleccionadas: {len(todas_columnas)}")
    print(f"   - Identificacion: {len(columnas_id)}")
    print(f"   - Numericas: {len(columnas_numericas)}")
    print(f"   - Categoricas: {len(columnas_categoricas)}")
    print(f"   - Flags: {len(columnas_flags)}")
    print(f"   - Target: {len(columnas_target)}")
    
    return df_modelo

def guardar_datos_con_features(df, ruta_salida):
    """Guarda el DataFrame con features en CSV"""
    df.to_csv(ruta_salida, index=False, encoding='utf-8-sig')
    print(f"\n✓ Datos con features guardados en: {ruta_salida}")

if __name__ == "__main__":
    # Rutas
    BASE_DIR = Path(__file__).parent.parent
    RUTA_ENTRADA = BASE_DIR / "data" / "datos_limpios.csv"
    RUTA_SALIDA = BASE_DIR / "data" / "datos_con_features.csv"
    
    # Cargar datos limpios
    print("\nCargando datos limpios...")
    df = pd.read_csv(RUTA_ENTRADA)
    print(f"Cargados {len(df)} leads")
    
    # Crear features
    df_features = crear_features(df)
    
    # Seleccionar columnas para modelo
    df_modelo = seleccionar_columnas_modelo(df_features)
    
    # Guardar
    guardar_datos_con_features(df_modelo, RUTA_SALIDA)
    
    print("\n" + "="*80)
    print("PROCESO COMPLETADO EXITOSAMENTE")
    print("="*80)
    print(f"\nArchivo final: {len(df_modelo)} leads, {len(df_modelo.columns)} columnas")
    print(f"Listo para entrenar el modelo!")
