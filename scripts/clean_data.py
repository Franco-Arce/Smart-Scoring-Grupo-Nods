"""
Script de Limpieza de Datos - Smart Scoring UNAB
Limpia y prepara los datos del CRM para el modelo de Machine Learning
"""

import pandas as pd
import numpy as np
import sys
import io
import re
from pathlib import Path

# Configurar encoding UTF-8
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def validar_email(email):
    """Valida si un email tiene formato correcto"""
    if pd.isna(email):
        return False
    # Patron basico de email
    patron = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(patron, str(email).strip()))

def limpiar_datos(ruta_archivo):
    """
    Limpia los datos del CRM
    
    Args:
        ruta_archivo: Path al archivo Excel del CRM
        
    Returns:
        DataFrame limpio
    """
    print("="*80)
    print("INICIANDO LIMPIEZA DE DATOS - SMART SCORING")
    print("="*80)
    
    # 1. Cargar datos
    print("\n[1/7] Cargando datos...")
    df = pd.read_excel(ruta_archivo)
    print(f"   -> Cargados {len(df)} leads")
    
    # 2. Eliminar columnas completamente vacias
    print("\n[2/7] Eliminando columnas vacias...")
    columnas_vacias = df.columns[df.isnull().all()].tolist()
    if columnas_vacias:
        print(f"   -> Eliminando: {columnas_vacias}")
        df = df.drop(columns=columnas_vacias)
    else:
        print("   -> No hay columnas completamente vacias")
    
    # 3. Crear variable objetivo (TARGET)
    print("\n[3/7] Creando variable objetivo (Matriculado)...")
    resoluciones_positivas = [
        'Matriculado',
        'Admitido',
        'En proceso de pago'
    ]
    df['target'] = df['Resolución'].apply(
        lambda x: 1 if str(x).strip() in resoluciones_positivas else 0
    )
    print(f"   -> Leads con target=1 (Matriculados): {df['target'].sum()}")
    print(f"   -> Leads con target=0 (No matriculados): {(df['target']==0).sum()}")
    print(f"   -> Tasa de conversion: {(df['target'].sum()/len(df)*100):.2f}%")
    
    # 4. Validar y limpiar emails
    print("\n[4/7] Validando emails...")
    df['email_valido'] = df['EMLMAIL'].apply(validar_email)
    emails_invalidos = (~df['email_valido']).sum()
    print(f"   -> Emails invalidos o faltantes: {emails_invalidos}")
    
    # 5. Detectar y eliminar duplicados (mismo email + mismo programa)
    print("\n[5/7] Detectando duplicados (mismo email + programa)...")
    # Solo consideramos duplicados si tienen email valido Y mismo programa
    df_con_email = df[df['email_valido']].copy()
    
    # Marcar duplicados basados en email + programa
    duplicados_mask = df_con_email.duplicated(
        subset=['EMLMAIL', 'Programa interes'], 
        keep='first'  # Mantener el primero
    )
    
    indices_duplicados = df_con_email[duplicados_mask].index
    print(f"   -> Duplicados encontrados: {len(indices_duplicados)}")
    
    # Eliminar duplicados
    df = df.drop(indices_duplicados)
    print(f"   -> Leads despues de eliminar duplicados: {len(df)}")
    
    # 6. Limpiar y normalizar campos de texto
    print("\n[6/7] Normalizando campos de texto...")
    
    # Programa de interes
    df['Programa interes'] = df['Programa interes'].fillna('NO ESPECIFICADO')
    df['Programa interes'] = df['Programa interes'].str.strip().str.upper()
    
    # Base de datos
    df['Base de datos'] = df['Base de datos'].str.strip()
    
    # UTM fields - normalizar
    for col in ['UTM Medium', 'UTM Source', 'UTM Campaing', 'UTM Content']:
        if col in df.columns:
            df[col] = df[col].fillna('no_disponible')
            df[col] = df[col].str.strip().str.lower()
    
    print("   -> Campos de texto normalizados")
    
    # 7. Manejar fechas
    print("\n[7/7] Procesando fechas...")
    df['Fecha insert Lead'] = pd.to_datetime(df['Fecha insert Lead'], errors='coerce')
    df['Fecha y hora de actualización'] = pd.to_datetime(
        df['Fecha y hora de actualización'], 
        errors='coerce'
    )
    
    # Calcular dias de gestion
    df['dias_gestion'] = (
        df['Fecha y hora de actualización'] - df['Fecha insert Lead']
    ).dt.days
    
    # Rellenar valores negativos o nulos con 0
    df['dias_gestion'] = df['dias_gestion'].fillna(0)
    df['dias_gestion'] = df['dias_gestion'].apply(lambda x: max(0, x))
    
    print(f"   -> Dias de gestion: min={df['dias_gestion'].min()}, "
          f"max={df['dias_gestion'].max()}, "
          f"promedio={df['dias_gestion'].mean():.1f}")
    
    print("\n" + "="*80)
    print("LIMPIEZA COMPLETADA")
    print("="*80)
    print(f"\nDataFrame final: {len(df)} leads, {len(df.columns)} columnas")
    print(f"Tasa de conversion: {(df['target'].sum()/len(df)*100):.2f}%")
    
    return df

def guardar_datos_limpios(df, ruta_salida):
    """Guarda el DataFrame limpio en CSV"""
    df.to_csv(ruta_salida, index=False, encoding='utf-8-sig')
    print(f"\n✓ Datos limpios guardados en: {ruta_salida}")

if __name__ == "__main__":
    # Rutas
    BASE_DIR = Path(__file__).parent.parent
    RUTA_ENTRADA = BASE_DIR / "data" / "Consulta_Base_Unificada_UNAB.xls"
    RUTA_SALIDA = BASE_DIR / "data" / "datos_limpios.csv"
    
    # Ejecutar limpieza
    df_limpio = limpiar_datos(RUTA_ENTRADA)
    
    # Guardar
    guardar_datos_limpios(df_limpio, RUTA_SALIDA)
    
    print("\n" + "="*80)
    print("PROCESO COMPLETADO EXITOSAMENTE")
    print("="*80)
