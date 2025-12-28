"""
Preparación de Datos Multi-Universidad - Smart Scoring
Combina y procesa datos de todas las universidades del Grupo Nods
"""

import pandas as pd
import numpy as np
import sys
import io
from pathlib import Path
import re
import json

# Configurar encoding UTF-8
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Cargar configuración de normalización
BASE_DIR = Path(__file__).parent.parent
CONFIG_PATH = BASE_DIR / "config" / "normalization_config.json"

with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
    NORMALIZATION_CONFIG = json.load(f)

def validar_email(email):
    """Valida si un email tiene formato correcto"""
    if pd.isna(email):
        return False
    patron = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(patron, str(email).strip()))

def normalizar_columnas(df, universidad_nombre=None):
    """
    Normaliza nombres de columnas para compatibilidad entre universidades
    Usa configuración centralizada de normalization_config.json
    """
    # 1. Eliminar espacios en nombres de columnas
    df.columns = df.columns.str.strip()
    
    # 2. Aplicar mapeo desde configuración
    mapeo_columnas = NORMALIZATION_CONFIG['column_mappings']
    
    # Log de mapeos aplicados
    mapeos_aplicados = []
    for col_origen, col_destino in mapeo_columnas.items():
        if col_origen in df.columns:
            mapeos_aplicados.append(f"{col_origen} → {col_destino}")
    
    if mapeos_aplicados and universidad_nombre:
        print(f"   📝 Mapeos aplicados en {universidad_nombre}:")
        for mapeo in mapeos_aplicados:
            print(f"      - {mapeo}")
    
    # Aplicar mapeo
    df = df.rename(columns=mapeo_columnas)
    
    # 3. Convertir CHKENTRANTEWHATSAPP (Si/No) a formato booleano
    if 'WhatsApp entrante' in df.columns:
        if df['WhatsApp entrante'].dtype == 'object':
            df['WhatsApp entrante'] = df['WhatsApp entrante'].apply(
                lambda x: 'entrante' if str(x).lower() in ['si', 'sí', 'yes', '1'] else None
            )
    
    return df

def normalizar_resoluciones(df):
    """
    Normaliza valores de Resolución usando configuración centralizada
    Crea columnas adicionales para categorías de resolución
    """
    if 'Resolución' not in df.columns:
        return df
    
    df_norm = df.copy()
    
    # Crear mapeo inverso: valor -> categoría
    valor_a_categoria = {}
    for categoria, valores in NORMALIZATION_CONFIG['resolution_mappings'].items():
        for valor in valores:
            valor_a_categoria[valor] = categoria
    
    # Aplicar categorización
    df_norm['resolucion_categoria'] = df_norm['Resolución'].apply(
        lambda x: valor_a_categoria.get(str(x).strip(), 'unknown') if pd.notna(x) else 'unknown'
    )
    
    # Crear target binario basado en categoría
    categoria_a_binario = NORMALIZATION_CONFIG['resolution_to_binary']
    df_norm['resolucion_binaria'] = df_norm['resolucion_categoria'].apply(
        lambda x: categoria_a_binario.get(x, 0)
    )
    
    return df_norm

def cargar_universidad(archivo_path, nombre_universidad):
    """
    Carga y preprocesa datos de una universidad
    """
    print(f"\n{'='*80}")
    print(f"CARGANDO: {nombre_universidad}")
    print(f"{'='*80}")
    
    try:
        # Cargar archivo
        df = pd.read_excel(archivo_path)
        print(f"✅ Cargados {len(df)} leads de {nombre_universidad}")
        
        # Normalizar columnas
        df = normalizar_columnas(df, nombre_universidad)
        
        # Eliminar columnas duplicadas (mantener primera ocurrencia)
        df = df.loc[:, ~df.columns.duplicated()]
        
        # Agregar columna de universidad
        df['universidad'] = nombre_universidad
        
        # Mostrar columnas únicas
        print(f"   Columnas: {len(df.columns)}")
        
        return df
        
    except Exception as e:
        print(f"❌ Error cargando {nombre_universidad}: {str(e)}")
        return None

def limpiar_datos_combinados(df):
    """
    Limpia los datos combinados de todas las universidades
    """
    print(f"\n{'='*80}")
    print("LIMPIANDO DATOS COMBINADOS")
    print(f"{'='*80}")
    
    df_limpio = df.copy()
    
    # 1. Eliminar columnas completamente vacías
    columnas_vacias = df_limpio.columns[df_limpio.isnull().all()].tolist()
    if columnas_vacias:
        df_limpio = df_limpio.drop(columns=columnas_vacias)
        print(f"✂️ Columnas vacías eliminadas: {len(columnas_vacias)}")
    
    # 2. Normalizar resoluciones y crear variable objetivo (TARGET)
    if 'Resolución' in df_limpio.columns:
        # Aplicar normalización de resoluciones
        df_limpio = normalizar_resoluciones(df_limpio)
        
        # Usar la resolución binaria normalizada como target
        df_limpio['target'] = df_limpio['resolucion_binaria']
        
        # Reportar valores no categorizados
        unknown_count = (df_limpio['resolucion_categoria'] == 'unknown').sum()
        if unknown_count > 0:
            print(f"\n⚠️  {unknown_count} resoluciones no categorizadas:")
            unknown_vals = df_limpio[df_limpio['resolucion_categoria'] == 'unknown']['Resolución'].value_counts().head(10)
            for val, count in unknown_vals.items():
                print(f"      - {val}: {count}")
        
        # Estadísticas por universidad
        print(f"\n📊 DISTRIBUCIÓN DE TARGET POR UNIVERSIDAD:")
        for uni in df_limpio['universidad'].unique():
            df_uni = df_limpio[df_limpio['universidad'] == uni]
            positivos = df_uni['target'].sum()
            tasa = (positivos / len(df_uni)) * 100 if len(df_uni) > 0 else 0
            print(f"   {uni:12s}: {positivos:5d} / {len(df_uni):6d} ({tasa:5.2f}%)")
    else:
        print("⚠️ No se encontró columna 'Resolución'")
        df_limpio['target'] = 0
    
    # 3. Validar y limpiar emails
    if 'EMLMAIL' in df_limpio.columns:
        df_limpio['email_valido'] = df_limpio['EMLMAIL'].apply(validar_email)
        emails_invalidos = (~df_limpio['email_valido']).sum()
        print(f"\n📧 Emails validados: {emails_invalidos} inválidos detectados")
    
    # 4. Detectar y eliminar duplicados (mismo email + mismo programa)
    if 'EMLMAIL' in df_limpio.columns and 'Programa interes' in df_limpio.columns:
        df_con_email = df_limpio[df_limpio['email_valido']].copy()
        duplicados_mask = df_con_email.duplicated(
            subset=['EMLMAIL', 'Programa interes'], 
            keep='first'
        )
        indices_duplicados = df_con_email[duplicados_mask].index
        
        if len(indices_duplicados) > 0:
            df_limpio = df_limpio.drop(indices_duplicados)
            print(f"🗑️ {len(indices_duplicados)} duplicados eliminados")
    
    # 5. Normalizar campos de texto y valores dentro de columnas
    print(f"\n🔄 Normalizando valores dentro de columnas...")
    
    # Normalizar Canal (wsp, WSP, Wsp, whatsapp, Whatsapp → todos a minúsculas)
    if 'Canal' in df_limpio.columns:
        df_limpio['Canal'] = df_limpio['Canal'].astype(str).str.strip().str.lower()
        # Unificar variaciones de WhatsApp
        df_limpio['Canal'] = df_limpio['Canal'].replace({
            'wsp': 'whatsapp',
            'whats': 'whatsapp',
            'wa': 'whatsapp',
            'nan': 'no_especificado'
        })
        print(f"   ✓ Canal normalizado")
    
    if 'Programa interes' in df_limpio.columns:
        df_limpio['Programa interes'] = df_limpio['Programa interes'].fillna('NO ESPECIFICADO')
        df_limpio['Programa interes'] = df_limpio['Programa interes'].astype(str).str.strip().str.upper()
        print(f"   ✓ Programa interes normalizado")
    
    if 'Base de datos' in df_limpio.columns:
        df_limpio['Base de datos'] = df_limpio['Base de datos'].astype(str).str.strip()
        print(f"   ✓ Base de datos normalizado")
    
    # Normalizar UTMs a minúsculas
    for col in ['UTM Medium', 'UTM Source', 'UTM Campaing', 'UTM Content']:
        if col in df_limpio.columns:
            df_limpio[col] = df_limpio[col].fillna('no_disponible')
            df_limpio[col] = df_limpio[col].astype(str).str.strip().str.lower()
            # Reemplazar 'nan' string con 'no_disponible'
            df_limpio[col] = df_limpio[col].replace('nan', 'no_disponible')
    
    print(f"   ✓ UTMs normalizados")
    
    # 6. Procesar fechas
    if 'Fecha insert Lead' in df_limpio.columns:
        df_limpio['Fecha insert Lead'] = pd.to_datetime(df_limpio['Fecha insert Lead'], errors='coerce')
    
    if 'Fecha y hora de actualización' in df_limpio.columns:
        df_limpio['Fecha y hora de actualización'] = pd.to_datetime(
            df_limpio['Fecha y hora de actualización'], errors='coerce'
        )
        
        # Calcular días de gestión
        if 'Fecha insert Lead' in df_limpio.columns:
            df_limpio['dias_gestion'] = (
                df_limpio['Fecha y hora de actualización'] - df_limpio['Fecha insert Lead']
            ).dt.days
            df_limpio['dias_gestion'] = df_limpio['dias_gestion'].fillna(0)
            df_limpio['dias_gestion'] = df_limpio['dias_gestion'].apply(lambda x: max(0, x))
    
    print(f"\n✅ Limpieza completada: {len(df_limpio)} leads listos")
    
    return df_limpio

def crear_features_multiuniversidad(df):
    """
    Crea features adicionales para el dataset multi-universidad
    """
    print(f"\n{'='*80}")
    print("CREANDO FEATURES")
    print(f"{'='*80}")
    
    df_features = df.copy()
    
    # 1. Features de Email
    if 'email_valido' in df_features.columns:
        df_features['tiene_email'] = df_features['email_valido'].astype(int)
    else:
        df_features['tiene_email'] = 0
    
    # 2. Features de WhatsApp
    if 'WhatsApp entrante' in df_features.columns:
        df_features['whatsapp_entrante_flag'] = df_features['WhatsApp entrante'].notna().astype(int)
    else:
        df_features['whatsapp_entrante_flag'] = 0
    
    # 3. Features Temporales
    if 'dias_gestion' in df_features.columns:
        df_features['lead_reciente'] = (df_features['dias_gestion'] < 7).astype(int)
        df_features['lead_antiguo'] = (df_features['dias_gestion'] > 30).astype(int)
    else:
        df_features['dias_gestion'] = 0
        df_features['lead_reciente'] = 0
        df_features['lead_antiguo'] = 0
    
    # 4. Features de Comportamiento
    if 'CONTADOR_LLAMADOS_TEL' in df_features.columns:
        df_features['ratio_llamadas_dias'] = df_features.apply(
            lambda row: row['CONTADOR_LLAMADOS_TEL'] / max(row.get('dias_gestion', 1), 1),
            axis=1
        )
        df_features['alta_actividad_llamadas'] = (df_features['CONTADOR_LLAMADOS_TEL'] > 5).astype(int)
    else:
        df_features['CONTADOR_LLAMADOS_TEL'] = 0
        df_features['ratio_llamadas_dias'] = 0
        df_features['alta_actividad_llamadas'] = 0
    
    if 'Llamadas_discador' not in df_features.columns:
        df_features['Llamadas_discador'] = 0
    
    # 5. Categorizar Programas
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
    
    if 'Programa interes' in df_features.columns:
        df_features['programa_categoria'] = df_features['Programa interes'].apply(categorizar_programa)
    else:
        df_features['programa_categoria'] = 'OTROS'
    
    # 6. Categorizar Base de Datos
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
    
    if 'Base de datos' in df_features.columns:
        df_features['base_categoria'] = df_features['Base de datos'].apply(categorizar_base)
    else:
        df_features['base_categoria'] = 'OTRO'
    
    # 7. Limpiar UTM Source
    def limpiar_utm_source(source):
        source_str = str(source).lower()
        if 'google' in source_str:
            return 'google'
        elif 'fb' in source_str or 'facebook' in source_str:
            return 'facebook'
        else:
            return 'otros'
    
    if 'UTM Source' in df_features.columns:
        df_features['utm_source_clean'] = df_features['UTM Source'].apply(limpiar_utm_source)
    else:
        df_features['utm_source_clean'] = 'otros'
    
    # 8. Limpiar UTM Medium
    def limpiar_utm_medium(medium):
        medium_str = str(medium).lower()
        if 'paid' in medium_str or 'social' in medium_str:
            return 'paid_social'
        elif 'organic' in medium_str:
            return 'organic'
        else:
            return 'otros'
    
    if 'UTM Medium' in df_features.columns:
        df_features['utm_medium_clean'] = df_features['UTM Medium'].apply(limpiar_utm_medium)
    else:
        df_features['utm_medium_clean'] = 'otros'
    
    print("✅ Features creadas exitosamente!")
    
    # Mostrar estadísticas por universidad
    print(f"\n📊 RESUMEN POR UNIVERSIDAD:")
    for uni in df_features['universidad'].unique():
        df_uni = df_features[df_features['universidad'] == uni]
        print(f"   {uni:12s}: {len(df_uni):6d} leads")
    
    return df_features

if __name__ == "__main__":
    # Rutas
    BASE_DIR = Path(__file__).parent.parent
    DATA_DIR = BASE_DIR / "data"
    
    print("="*80)
    print("PREPARACIÓN DE DATOS MULTI-UNIVERSIDAD")
    print("="*80)
    
    # Archivos de cada universidad
    archivos_universidades = {
        'UNAB': DATA_DIR / 'Consulta_Base_Unificada_UNAB.xls',
        'Crexe': DATA_DIR / 'Reporte_Bases_Unificadas_Crexe.xls',
        'UEES': DATA_DIR / 'Consulta_Base_Unificada_UEES.xls',
        'Anahuac': DATA_DIR / 'Consulta_Base_Unificada_Anahuac.xls',
        'Unisangil': DATA_DIR / 'Consulta_Base_Unificada_Unisangil.xls'
    }
    
    # Cargar todas las universidades
    dataframes = []
    for nombre, archivo in archivos_universidades.items():
        if archivo.exists():
            df_uni = cargar_universidad(archivo, nombre)
            if df_uni is not None:
                dataframes.append(df_uni)
        else:
            print(f"⚠️ Archivo no encontrado: {archivo}")
    
    # Combinar todos los dataframes
    print(f"\n{'='*80}")
    print("COMBINANDO DATASETS")
    print(f"{'='*80}")
    
    df_combinado = pd.concat(dataframes, ignore_index=True)
    print(f"✅ Total combinado: {len(df_combinado)} leads de {len(dataframes)} universidades")
    
    # Limpiar datos
    df_limpio = limpiar_datos_combinados(df_combinado)
    
    # Guardar datos limpios
    ruta_limpios = DATA_DIR / "datos_multi_universidad_limpios.csv"
    df_limpio.to_csv(ruta_limpios, index=False, encoding='utf-8-sig')
    print(f"\n💾 Datos limpios guardados: {ruta_limpios}")
    
    # Crear features
    df_features = crear_features_multiuniversidad(df_limpio)
    
    # Guardar datos con features
    ruta_features = DATA_DIR / "datos_multi_universidad_features.csv"
    df_features.to_csv(ruta_features, index=False, encoding='utf-8-sig')
    print(f"💾 Datos con features guardados: {ruta_features}")
    
    print(f"\n{'='*80}")
    print("PROCESO COMPLETADO EXITOSAMENTE")
    print(f"{'='*80}")
    print(f"\n📊 RESUMEN FINAL:")
    print(f"   Total leads: {len(df_features):,}")
    print(f"   Universidades: {df_features['universidad'].nunique()}")
    print(f"   Features: {len(df_features.columns)}")
    print(f"   Target positivos: {df_features['target'].sum():,} ({df_features['target'].mean()*100:.2f}%)")
