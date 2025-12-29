"""
Smart Scoring UNAB - Aplicacion de Lead Scoring Predictivo
Interfaz web para predecir probabilidad de matricula de leads
VERSION 2.0 - Con procesamiento automático de archivos del CRM
"""

import streamlit as st
import pandas as pd
import numpy as np
import pickle
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path
import sys
import re

# Configurar la pagina
st.set_page_config(
    page_title="Smart Scoring Grupo Nods",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS personalizado para diseño premium
st.markdown("""
<style>
    /* Fondo y tema oscuro */
    .main {
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
    }
    
    /* Titulo principal */
    h1 {
        color: #00d9ff;
        font-weight: 700;
        text-shadow: 0 0 20px rgba(0, 217, 255, 0.5);
        padding: 20px 0;
    }
    
    /* Subtitulos */
    h2, h3 {
        color: #ffffff;
        font-weight: 600;
    }
    
    /* Metricas */
    [data-testid="stMetricValue"] {
        font-size: 2rem;
        color: #00d9ff;
    }
    
    /* Cards */
    .stAlert {
        background-color: rgba(255, 255, 255, 0.05);
        border-left: 4px solid #00d9ff;
        backdrop-filter: blur(10px);
    }
    
    /* Botones */
    .stButton>button {
        background: linear-gradient(90deg, #00d9ff 0%, #0099cc 100%);
        color: white;
        font-weight: 600;
        border: none;
        padding: 12px 24px;
        border-radius: 8px;
        box-shadow: 0 4px 15px rgba(0, 217, 255, 0.3);
        transition: all 0.3s ease;
    }
    
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(0, 217, 255, 0.5);
    }
    
    /* Tablas */
    .dataframe {
        background-color: rgba(255, 255, 255, 0.05) !important;
        backdrop-filter: blur(10px);
    }
    
    /* Sidebar */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0f3460 0%, #16213e 100%);
    }
</style>
""", unsafe_allow_html=True)

# Funciones para cargar modelo
@st.cache_resource
def cargar_modelo():
    """Carga el modelo limpio multi-universidad (SIN data leakage)"""
    BASE_DIR = Path(__file__).parent
    modelo_path = BASE_DIR / "models" / "modelo_scoring_sin_leakage.pkl"
    encoders_path = BASE_DIR / "models" / "label_encoders_sin_leakage.pkl"
    
    with open(modelo_path, 'rb') as f:
        modelo = pickle.load(f)
    
    with open(encoders_path, 'rb') as f:
        encoders = pickle.load(f)
    
    return modelo, encoders

# ===== FUNCIONES DE NORMALIZACION MULTI-UNIVERSIDAD =====

def detectar_universidad(df):
    """
    Detecta automáticamente la universidad basándose en características del dataset
    Returns: 'UNAB', 'Crexe', 'UEES', 'Anahuac', 'Unisangil', 'Desconocido'
    """
    # Método 0: Analizar columna "Base de datos" (MÁS CONFIABLE)
    if 'Base de datos' in df.columns:
        bases_str = ' '.join(df['Base de datos'].astype(str).str.upper().unique())
        
        # Buscar nombres de universidades en las bases de datos
        # Orden de prioridad: buscar patrones más específicos primero
        if 'UNAB' in bases_str:
            return 'UNAB'
        elif 'CREXE' in bases_str:
            return 'Crexe'
        elif 'UEES' in bases_str:
            return 'UEES'
        elif 'ANAHUAC' in bases_str or 'ANÁHUAC' in bases_str:
            return 'Anahuac'
        elif 'UNISANGIL' in bases_str or 'SANGIL' in bases_str:
            return 'Unisangil'
    
    # Método 1: Analizar características específicas de columnas
    col_names = [str(c).lower() for c in df.columns]
    
    # UEES tiene columnas únicas
    if 'operador' in col_names and 'nombre operador' in col_names:
        return 'UEES'
    
    # Crexe tiene CHKENTRANTEWHATSAPP antes de normalizar
    if 'chkentrantewhatsapp' in col_names or 'txtestadoprincipal' in col_names:
        return 'Crexe'
    
    # Método 2: Analizar programas únicos
    if 'Programa interes' in df.columns or 'programa interes' in col_names:
        programas = df['Programa interes'].astype(str).str.upper() if 'Programa interes' in df.columns else []
        programas_str = ' '.join(programas.unique())
        
        # Programas específicos de cada universidad
        if 'NEUROCIENCIA' in programas_str or 'MINDFULNESS' in programas_str:
            return 'Crexe'
        elif 'ANAHUAC' in programas_str:
            return 'Anahuac'
        elif 'UNISANGIL' in programas_str:
            return 'Unisangil'
    
    # Método 3: Por cantidad de leads (ÚLTIMO RECURSO - menos confiable)
    # Solo usar si ningún otro método funcionó
    if len(df) > 40000:
        return 'Crexe'  # Crexe tiene ~44K leads
    elif len(df) > 25000:
        return 'UEES'  # UEES tiene ~27K leads
    elif len(df) > 10000:
        return 'Anahuac'  # Anahuac tiene ~15K leads
    elif len(df) > 5000:
        return 'UNAB'  # UNAB tiene ~6K leads
    else:
        return 'Unisangil'  # Unisangil tiene ~4K leads

def normalizar_columnas(df):
    """
    Normaliza nombres de columnas para compatibilidad entre universidades
    - Elimina espacios al inicio/final
    - Mapea nombres comunes entre diferentes CRMs
    - Soporta: UNAB, Crexe, UEES y otras instituciones
    """
    # 1. Eliminar espacios en nombres de columnas
    df.columns = df.columns.str.strip()
    
    # 2. Mapeo de columnas con nombres diferentes
    mapeo_columnas = {
        # Crexe/UEES -> UNAB (estandar)
        'Idcontacto': 'dcontacto',
        'Lamadas_discador': 'Llamadas_discador',  # Typo en Crexe/UEES
        'CHKENTRANTEWHATSAPP': 'WhatsApp entrante',
        'TXTESTADOPRINCIPAL': 'Estado principal',
        'Ultima resolucion': 'Ultima resolución',
        
        # UEES específico
        'Contador de Llamadas': 'CONTADOR_LLAMADOS_TEL',
        'Fecha Inserción Leads': 'Fecha insert Lead',
        'UTM Origen': 'UTM Source',  # UEES usa "Origen" en vez de "Source"
        
        # Otras variaciones comunes
        'Resolucion': 'Resolución',
        'Fecha y hora de actualizacion': 'Fecha y hora de actualización',
        'Programa interes': 'Programa interes',  # Ya normalizado
    }
    
    # Aplicar mapeo
    df = df.rename(columns=mapeo_columnas)
    
    # 3. Convertir CHKENTRANTEWHATSAPP (Si/No) a formato booleano
    if 'WhatsApp entrante' in df.columns:
        # Si es texto "Si"/"No", convertir
        if df['WhatsApp entrante'].dtype == 'object':
            df['WhatsApp entrante'] = df['WhatsApp entrante'].apply(
                lambda x: 'entrante' if str(x).lower() in ['si', 'sí', 'yes', '1'] else None
            )
    
    return df

# ===== FUNCIONES DE PROCESAMIENTO INTEGRADAS =====

def validar_email(email):
    """Valida si un email tiene formato correcto"""
    if pd.isna(email):
        return False
    patron = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(patron, str(email).strip()))

def limpiar_datos_integrado(df):
    """Limpia los datos del CRM (versión integrada para Streamlit)"""
    
    with st.spinner("🧹 Limpiando datos..."):
        # 0. NORMALIZAR COLUMNAS (Multi-universidad)
        st.info("🔄 Normalizando formato de columnas...")
        df_limpio = normalizar_columnas(df.copy())
        
        # 1. Eliminar columnas completamente vacías
        columnas_vacias = df_limpio.columns[df_limpio.isnull().all()].tolist()
        if columnas_vacias:
            df_limpio = df_limpio.drop(columns=columnas_vacias)
            st.info(f"✂️ Columnas vacías eliminadas: {', '.join(columnas_vacias)}")
        
        # 2. Crear variable objetivo (TARGET)
        if 'Resolución' in df_limpio.columns:
            resoluciones_positivas = ['Matriculado', 'Admitido', 'En proceso de pago']
            df_limpio['target'] = df_limpio['Resolución'].apply(
                lambda x: 1 if str(x).strip() in resoluciones_positivas else 0
            )
            st.success(f"✅ Variable objetivo creada: {df_limpio['target'].sum()} matriculados ({df_limpio['target'].mean()*100:.2f}%)")
        else:
            st.warning("⚠️ No se encontró columna 'Resolución' - creando target = 0")
        
        # 3. Validar y limpiar emails
        if 'EMLMAIL' in df_limpio.columns:
            df_limpio['email_valido'] = df_limpio['EMLMAIL'].apply(validar_email)
            emails_invalidos = (~df_limpio['email_valido']).sum()
            st.info(f"📧 Emails validados: {emails_invalidos} inválidos detectados")
        
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
                st.warning(f"🗑️ {len(indices_duplicados)} duplicados eliminados (mismo email + programa)")
        
        # 5. Normalizar campos de texto
        if 'Programa interes' in df_limpio.columns:
            df_limpio['Programa interes'] = df_limpio['Programa interes'].fillna('NO ESPECIFICADO')
            df_limpio['Programa interes'] = df_limpio['Programa interes'].str.strip().str.upper()
        
        if 'Base de datos' in df_limpio.columns:
            df_limpio['Base de datos'] = df_limpio['Base de datos'].str.strip()
        
        for col in ['UTM Medium', 'UTM Source', 'UTM Campaing', 'UTM Content']:
            if col in df_limpio.columns:
                df_limpio[col] = df_limpio[col].fillna('no_disponible')
                df_limpio[col] = df_limpio[col].str.strip().str.lower()
        
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
        
        st.success(f"✅ Limpieza completada: {len(df_limpio)} leads listos")
    
    return df_limpio

def crear_features_integrado(df):
    """Crea features adicionales (versión integrada para Streamlit)"""
    
    with st.spinner("🔧 Creando features..."):
        df_features = df.copy()
        
        # 0. DETECTAR Y AGREGAR UNIVERSIDAD
        if 'universidad' not in df_features.columns:
            # Priorizar selección manual del usuario
            if 'universidad_manual' in st.session_state and st.session_state['universidad_manual'] != "Detección Automática":
                universidad_detectada = st.session_state['universidad_manual']
                st.success(f"🎓 Universidad seleccionada manualmente: **{universidad_detectada}**")
            else:
                # Detección automática
                universidad_detectada = detectar_universidad(df_features)
                st.info(f"🎓 Universidad detectada automáticamente: **{universidad_detectada}**")
            
            df_features['universidad'] = universidad_detectada

        
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
            
            # Casos especiales primero
            if programa_str in ['NO ESPECIFICADO', 'NAN', 'NONE', '']:
                return 'NO_ESPECIFICADO'
            
            # Tecnología
            if 'TECNOLOGÍA' in programa_str or 'TECNOLOGIA' in programa_str:
                return 'TECNOLOGIA'
            
            # Posgrados
            elif 'ESPECIALIZACIÓN' in programa_str or 'ESPECIALIZACION' in programa_str:
                return 'ESPECIALIZACION'
            elif 'MAESTRÍA' in programa_str or 'MAESTRIA' in programa_str:
                return 'MAESTRIA'
            elif 'DOCTORADO' in programa_str:
                return 'DOCTORADO'
            
            # Áreas específicas
            elif 'DERECHO' in programa_str:
                return 'DERECHO'
            elif 'ADMINISTR' in programa_str or 'NEGOCIO' in programa_str or 'CONTAD' in programa_str or 'EMPRESA' in programa_str:
                return 'NEGOCIOS'
            elif 'SALUD' in programa_str or 'FARMACIA' in programa_str or 'EPIDEMIO' in programa_str or 'MEDICINA' in programa_str or 'ENFERM' in programa_str:
                return 'SALUD'
            elif 'INGENIER' in programa_str:
                return 'INGENIERIA'
            elif 'EDUCAC' in programa_str or 'PEDAGOG' in programa_str:
                return 'EDUCACION'
            elif 'ARTE' in programa_str or 'DISEÑO' in programa_str or 'DISENO' in programa_str or 'AUDIOVISUAL' in programa_str or 'LITERATURA' in programa_str:
                return 'ARTE_DISENO'
            elif 'PSICOLOG' in programa_str or 'SOCIAL' in programa_str:
                return 'CIENCIAS_SOCIALES'
            else:
                return 'OTROS'
        
        if 'Programa interes' in df_features.columns:
            df_features['programa_categoria'] = df_features['Programa interes'].apply(categorizar_programa)
        else:
            df_features['programa_categoria'] = 'OTROS'
        
        # 6. Categorizar Base de Datos
        def categorizar_base(base):
            base_str = str(base).upper()
            
            # Casos especiales
            if base_str in ['NAN', 'NONE', '']:
                return 'NO_ESPECIFICADO'
            
            # Categorías principales
            if 'PREGRADO' in base_str:
                return 'PREGRADO'
            elif 'POSGRADO' in base_str or 'POSTGRADO' in base_str:
                return 'POSGRADO'
            elif 'LETO' in base_str:
                return 'LETO'
            
            # Detectar por número de base (UNAB usa números)
            elif 'CONSOLIDADO' in base_str or 'CONSOLIDADA' in base_str:
                return 'BASE_CONSOLIDADA'
            elif 'PRUEBA' in base_str or 'TEST' in base_str:
                return 'BASE_PRUEBA'
            elif 'RMK' in base_str or 'REMARKETING' in base_str:
                return 'REMARKETING'
            
            # Detectar bases numeradas (ej: "101 - BBDD")
            elif any(num in base_str for num in ['101', '102', '103', '104', '105']):
                return 'BASE_PRINCIPAL'
            elif any(num in base_str for num in ['22', '23', '24', '25']):
                return 'BASE_SECUNDARIA'
            
            else:
                return 'OTRO'
        
        if 'Base de datos' in df_features.columns:
            df_features['base_categoria'] = df_features['Base de datos'].apply(categorizar_base)
        else:
            df_features['base_categoria'] = 'OTRO'
        
        # 7. Limpiar UTM Source
        def limpiar_utm_source(source):
            source_str = str(source).lower().strip()
            
            # Valores vacíos o no disponibles
            if source_str in ['no_disponible', 'nan', 'none', '', 'no disponible']:
                return 'no_disponible'
            
            # Fuentes conocidas
            if 'google' in source_str:
                return 'google'
            elif 'fb' in source_str or 'facebook' in source_str:
                return 'facebook'
            elif 'instagram' in source_str or 'ig' in source_str:
                return 'instagram'
            elif 'linkedin' in source_str:
                return 'linkedin'
            elif 'twitter' in source_str or 'x.com' in source_str:
                return 'twitter'
            elif 'tiktok' in source_str:
                return 'tiktok'
            elif 'youtube' in source_str or 'yt' in source_str:
                return 'youtube'
            elif 'email' in source_str or 'correo' in source_str:
                return 'email'
            elif 'direct' in source_str or 'directo' in source_str:
                return 'directo'
            else:
                return 'otros'
        
        if 'UTM Source' in df_features.columns:
            df_features['utm_source_clean'] = df_features['UTM Source'].apply(limpiar_utm_source)
        else:
            df_features['utm_source_clean'] = 'otros'
        
        # 8. Limpiar UTM Medium
        def limpiar_utm_medium(medium):
            medium_str = str(medium).lower().strip()
            
            # Valores vacíos o no disponibles
            if medium_str in ['no_disponible', 'nan', 'none', '', 'no disponible', 'test']:
                return 'no_disponible'
            
            # Medios conocidos
            if 'paid' in medium_str:
                return 'paid'
            elif 'social' in medium_str:
                return 'social'
            elif 'organic' in medium_str or 'organico' in medium_str:
                return 'organic'
            elif 'cpc' in medium_str or 'ppc' in medium_str:
                return 'cpc'
            elif 'email' in medium_str or 'correo' in medium_str:
                return 'email'
            elif 'referral' in medium_str or 'referido' in medium_str:
                return 'referral'
            elif 'display' in medium_str or 'banner' in medium_str:
                return 'display'
            else:
                return 'otros'
        
        if 'UTM Medium' in df_features.columns:
            df_features['utm_medium_clean'] = df_features['UTM Medium'].apply(limpiar_utm_medium)
        else:
            df_features['utm_medium_clean'] = 'otros'
        
        st.success("✅ Features creadas exitosamente!")
    
    return df_features

def detectar_tipo_archivo(df):
    """
    Detecta si el archivo ya está procesado o si es del CRM original
    Returns: 'procesado', 'crm_original', 'desconocido'
    """
    # Columnas que debe tener un archivo procesado
    columnas_procesadas = [
        'programa_categoria', 'base_categoria', 
        'utm_source_clean', 'utm_medium_clean',
        'ratio_llamadas_dias'
    ]
    
    # Columnas típicas del CRM original
    columnas_crm = ['dcontacto', 'Nombre y Apellido', 'TELTELEFONO', 'Resolución']
    
    tiene_procesadas = all(col in df.columns for col in columnas_procesadas)
    tiene_crm = any(col in df.columns for col in columnas_crm)
    
    if tiene_procesadas:
        return 'procesado'
    elif tiene_crm:
        return 'crm_original'
    else:
        return 'desconocido'

def preparar_datos_prediccion(df, encoders):
    """
    Prepara los datos para prediccion (mismo proceso que entrenamiento)
    IMPORTANTE: El orden de las columnas debe coincidir EXACTAMENTE con el entrenamiento
    """
    # Codificar categoricas PRIMERO (incluye universidad)
    columnas_categoricas = ['universidad', 'programa_categoria', 'base_categoria', 'utm_source_clean', 'utm_medium_clean']
    
    df_encoded = df.copy()
    
    for col in columnas_categoricas:
        if col in df_encoded.columns and col in encoders:
            le = encoders[col]
            # Manejar categorias nuevas
            df_encoded[col] = df_encoded[col].apply(
                lambda x: x if x in le.classes_ else le.classes_[0]
            )
            df_encoded[col] = le.transform(df_encoded[col])
        elif col not in df_encoded.columns:
            st.warning(f"⚠️ Columna {col} no encontrada, usando valor por defecto")
            df_encoded[col] = 0
    
    # ORDEN EXACTO de columnas como en el entrenamiento
    # Este orden fue extraído directamente del modelo entrenado
    columnas_modelo_orden = [
        'universidad',
        'CONTADOR_LLAMADOS_TEL',
        'Llamadas_discador',
        'dias_gestion',
        'ratio_llamadas_dias',
        'alta_actividad_llamadas',  # IMPORTANTE: va aquí, no al final
        'lead_reciente',
        'lead_antiguo',
        'tiene_email',
        'whatsapp_entrante_flag',
        'programa_categoria',
        'base_categoria',
        'utm_source_clean',
        'utm_medium_clean'
    ]
    
    # Verificar que todas las columnas existen
    columnas_faltantes = [col for col in columnas_modelo_orden if col not in df_encoded.columns]
    if columnas_faltantes:
        st.error(f"❌ Faltan columnas necesarias: {columnas_faltantes}")
        st.info("💡 Asegurate de que el archivo esté en el formato correcto.")
        return None
    
    # Seleccionar columnas EN EL ORDEN CORRECTO
    X = df_encoded[columnas_modelo_orden].copy()
    
    return X

def generar_visualizaciones_y_resultados(df):
    """Genera métricas, gráficos y tablas de resultados"""
    
    # Ordenar por probabilidad
    df_sorted = df.sort_values('Probabilidad_Matricula', ascending=False)
    
    st.success("✅ Scores generados exitosamente!")
    
    # Métricas principales
    st.markdown("## 📊 Resumen de Resultados")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Leads", f"{len(df):,}")
    
    with col2:
        altos = (df['Probabilidad_Matricula'] > 60).sum()
        st.metric("Alto Potencial", f"{altos:,}", delta=f"{(altos/len(df)*100):.1f}%")
    
    with col3:
        st.metric("Score Promedio", f"{df['Probabilidad_Matricula'].mean():.1f}%")
    
    with col4:
        st.metric("Score Máximo", f"{df['Probabilidad_Matricula'].max():.1f}%")
    
    # Gráficos
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 📊 Distribución de Scores")
        fig_hist = px.histogram(
            df, x='Probabilidad_Matricula', nbins=30,
            color_discrete_sequence=['#00d9ff'], template='plotly_dark'
        )
        fig_hist.update_layout(
            xaxis_title="Probabilidad de Matrícula (%)",
            yaxis_title="Cantidad de Leads",
            showlegend=False
        )
        st.plotly_chart(fig_hist, use_container_width=True)
    
    with col2:
        st.markdown("### 🎯 Distribución por Categoría")
        categoria_counts = df['Score_Categoria'].value_counts()
        fig_pie = px.pie(
            values=categoria_counts.values, names=categoria_counts.index,
            color_discrete_sequence=['#ff6b6b', '#feca57', '#48dbfb'],
            template='plotly_dark'
        )
        st.plotly_chart(fig_pie, use_container_width=True)
    
    # Top 20 Leads
    st.markdown("---")
    st.markdown("### 🏆 Top 20 Leads con Mayor Probabilidad")
    
    columnas_mostrar = [
        'dcontacto', 'Nombre y Apellido', 'TELTELEFONO', 
        'Programa interes', 'Probabilidad_Matricula', 'Score_Categoria'
    ]
    
    columnas_disponibles = [col for col in columnas_mostrar if col in df_sorted.columns]
    
    st.dataframe(
        df_sorted[columnas_disponibles].head(20),
        use_container_width=True,
        hide_index=True
    )
    
    # Descargar resultados
    st.markdown("---")
    st.markdown("### 💾 Descargar Resultados")
    
    csv = df_sorted.to_csv(index=False, encoding='utf-8-sig')
    
    st.download_button(
        label="📥 Descargar CSV con Scores",
        data=csv,
        file_name="leads_con_scores.csv",
        mime="text/csv",
        use_container_width=True
    )

def main():
    # Header con animacion
    st.markdown("<h1 style='text-align: center;'>🎓 Smart Scoring Grupo Nods</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #00d9ff; font-size: 1.2rem;'>Sistema Automatizado de Lead Scoring Predictivo</p>", unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Sidebar con selector de universidad
    with st.sidebar:
        st.markdown("### 🎓 Smart Scoring")
        st.markdown("Sistema de Lead Scoring para Grupo Nods")
        
        st.markdown("---")
        st.markdown("### 🏫 Selección de Universidad")
        
        # Selector manual de universidad
        universidad_manual = st.selectbox(
            "Seleccioná la universidad:",
            options=["Detección Automática", "UNAB", "Crexe", "UEES", "Anahuac", "Unisangil"],
            help="Seleccioná manualmente la universidad o dejá que el sistema la detecte automáticamente"
        )
        
        # Guardar en session state
        st.session_state['universidad_manual'] = universidad_manual
        
        if universidad_manual != "Detección Automática":
            st.info(f"✅ Universidad seleccionada: **{universidad_manual}**")
        
        st.markdown("---")
        st.markdown("### 📊 Universidades Soportadas")
        st.markdown("""
        - ✅ UNAB
        - ✅ Crexe  
        - ✅ UEES
        - ✅ Anahuac
        - ✅ Unisangil
        """)
        
        st.markdown("---")
        st.markdown("### 💡 Instrucciones")
        st.markdown("""
        1. Seleccioná la universidad (opcional)
        2. Subí el archivo del CRM
        3. Procesá los datos
        4. Generá los scores
        5. Descargá los resultados
        """)
    
    # Contenido principal - Solo modo Upload
    if True:  # Siempre modo upload
        st.markdown("## 📤 Subir Archivo de Leads")
        
        st.info("""
        💡 **Compatibilidad Multi-Universidad**
        
        La app funciona con archivos de **cualquier universidad** del Grupo Nods:
        - ✅ UNAB
        - ✅ Crexe
        - ✅ UEES
        - ✅ Otras instituciones con estructura similar
        
        Podés subir **directamente el archivo del CRM** (Excel o CSV) y la app lo procesará automáticamente.
        También podés subir archivos ya procesados con features.
        """)
        
        uploaded_file = st.file_uploader(
            "Arrastrá o seleccioná el archivo",
            type=['csv', 'xls', 'xlsx'],
            help="Archivo del CRM Neotel o CSV ya procesado"
        )
        
        if uploaded_file is not None:
            # Cargar datos (detectar tipo de archivo)
            try:
                if uploaded_file.name.endswith('.csv'):
                    df = pd.read_csv(uploaded_file)
                else:
                    df = pd.read_excel(uploaded_file)
                
                st.success(f"✅ Archivo cargado: {len(df)} leads")
                
                # Detectar tipo de archivo
                tipo_archivo = detectar_tipo_archivo(df)
                
                if tipo_archivo == 'procesado':
                    st.markdown("<p class='ready-badge'>✅ Archivo YA procesado - Listo para predecir</p>", unsafe_allow_html=True)
                    df_procesado = df
                    mostrar_predicciones = True
                    
                elif tipo_archivo == 'crm_original':
                    st.markdown("<p class='processing-badge'>⚠️ Archivo del CRM detectado - Requiere procesamiento</p>", unsafe_allow_html=True)
                    
                    # Mostrar vista previa
                    with st.expander("👁️ Vista Previa de Datos Originales"):
                        st.dataframe(df.head(5), use_container_width=True)
                    
                    # Botón para procesar
                    if st.button("🔧 PROCESAR DATOS", use_container_width=True, type="primary"):
                        # Procesar datos
                        df_limpio = limpiar_datos_integrado(df)
                        df_procesado = crear_features_integrado(df_limpio)
                        
                        # Guardar en session state
                        st.session_state['df_procesado'] = df_procesado
                        st.session_state['mostrar_predicciones'] = True
                        st.rerun()
                    
                    mostrar_predicciones = False
                    
                    # Si ya está en session state
                    if 'df_procesado' in st.session_state and st.session_state.get('mostrar_predicciones', False):
                        df_procesado = st.session_state['df_procesado']
                        mostrar_predicciones = True
                        st.success("✅ Datos procesados correctamente!")
                    
                else:
                    st.error("❌ No se pudo detectar el formato del archivo. Asegurate de subir un archivo del CRM Neotel o un CSV procesado.")
                    mostrar_predicciones = False
                
                # Generar predicciones
                if mostrar_predicciones:
                    st.markdown("---")
                    
                    # Vista previa de datos procesados
                    with st.expander("👁️ Vista Previa de Datos Procesados"):
                        st.dataframe(df_procesado.head(10), use_container_width=True)
                    
                    if st.button("🚀 GENERAR SCORES", use_container_width=True, type="primary"):
                        with st.spinner("🤖 Modelo trabajando..."):
                            # Cargar modelo
                            modelo, encoders = cargar_modelo()
                            
                            # Preparar datos
                            X = preparar_datos_prediccion(df_procesado, encoders)
                            
                            if X is not None:
                                # Predecir
                                probabilidades = modelo.predict_proba(X)[:, 1]
                                
                                # Agregar scores
                                df_procesado['Probabilidad_Matricula'] = (probabilidades * 100).round(2)
                                df_procesado['Score_Categoria'] = pd.cut(
                                    df_procesado['Probabilidad_Matricula'],
                                    bins=[0, 30, 60, 100],
                                    labels=['⭐ Bajo', '⭐⭐ Medio', '⭐⭐⭐ Alto']
                                )
                                
                                # Generar visualizaciones
                                generar_visualizaciones_y_resultados(df_procesado)
                
            except Exception as e:
                st.error(f"❌ Error al cargar el archivo: {str(e)}")
                st.info("💡 Asegurate de que el archivo esté en el formato correcto.")
    


if __name__ == "__main__":
    main()
