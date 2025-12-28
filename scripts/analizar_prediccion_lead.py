"""
Análisis detallado de predicción para Lead ID 13535
Desglose de features y contribución al score
"""

import pandas as pd
import pickle
import numpy as np

# Cargar modelo y encoders
modelo = pickle.load(open('models/modelo_scoring_sin_leakage.pkl', 'rb'))
encoders = pickle.load(open('models/label_encoders_sin_leakage.pkl', 'rb'))

# Cargar datos procesados
df = pd.read_csv('data/datos_multi_universidad_features.csv', low_memory=False)

# Buscar el lead 13535 de Anahuac
lead = df[(df['dcontacto'] == 13535) & (df['universidad'] == 'Anahuac')]

if len(lead) > 0:
    print("="*80)
    print("ANÁLISIS DETALLADO - LEAD ID 13535 (Paola Torres García)")
    print("="*80)
    
    # Features que el modelo VE (sin data leakage)
    print("\n FEATURES QUE EL MODELO USA (SIN DATA LEAKAGE):")
    print("-"*80)
    
    features_modelo = [
        'universidad',
        'CONTADOR_LLAMADOS_TEL',
        'Llamadas_discador',
        'dias_gestion',
        'ratio_llamadas_dias',
        'alta_actividad_llamadas',
        'lead_reciente',
        'lead_antiguo',
        'tiene_email',
        'whatsapp_entrante_flag',
        'programa_categoria',
        'base_categoria',
        'utm_source_clean',
        'utm_medium_clean'
    ]
    
    for feat in features_modelo:
        if feat in lead.columns:
            valor = lead[feat].values[0]
            print(f"  {feat:30s}: {valor}")
    
    # Preparar datos para predicción
    X_lead = lead[features_modelo].copy()
    
    # Codificar categóricas
    columnas_categoricas = ['universidad', 'programa_categoria', 'base_categoria', 'utm_source_clean', 'utm_medium_clean']
    
    for col in columnas_categoricas:
        if col in encoders:
            le = encoders[col]
            X_lead[col] = X_lead[col].apply(
                lambda x: x if x in le.classes_ else le.classes_[0]
            )
            X_lead[col] = le.transform(X_lead[col])
    
    # Predecir
    probabilidad = modelo.predict_proba(X_lead)[0, 1] * 100
    
    print("\n" + "="*80)
    print(f"PROBABILIDAD PREDICHA: {probabilidad:.2f}%")
    print("="*80)
    
    # Obtener importancia de features
    feature_importance = modelo.feature_importances_
    
    print("\n CONTRIBUCIÓN DE CADA FEATURE (Importancia en el modelo):")
    print("-"*80)
    
    for feat, imp in sorted(zip(features_modelo, feature_importance), key=lambda x: x[1], reverse=True):
        valor = X_lead[feat].values[0]
        print(f"  {feat:30s}: {imp*100:5.2f}% | Valor: {valor}")
    
    # Análisis específico
    print("\n" + "="*80)
    print(" ANÁLISIS DETALLADO DEL SCORE (44.4%)")
    print("="*80)
    
    print("\n FACTORES POSITIVOS:")
    if lead['CONTADOR_LLAMADOS_TEL'].values[0] > 5:
        print(f"  • Alta actividad de llamadas: {lead['CONTADOR_LLAMADOS_TEL'].values[0]} llamadas")
    if lead['universidad'].values[0] == 'Anahuac':
        print(f"  • Universidad Anahuac (tasa conversión: 1.67%)")
    if lead['alta_actividad_llamadas'].values[0] == 1:
        print(f"  • Flag de alta actividad activado")
    
    print("\n FACTORES NEGATIVOS:")
    if lead['tiene_email'].values[0] == 0:
        print(f"  • NO tiene email válido (reduce probabilidad)")
    if lead['programa_categoria'].values[0] == 'OTROS':
        print(f"  • Programa no especificado (categoría OTROS)")
    if lead['whatsapp_entrante_flag'].values[0] == 0:
        print(f"  • NO tiene WhatsApp entrante")
    
    print("\n INTERPRETACIÓN:")
    print("-"*80)
    print(f"""
El modelo le asignó 44.4% porque:

1. **Universidad Anahuac** (44.3% importancia): Tiene tasa de conversión de 1.67%
2. **21 llamadas realizadas** (7.7% importancia): Muestra interés y gestión activa
3. **Ratio llamadas/días** (9.9% importancia): Alta frecuencia de contacto
4. **Programa no especificado** (12.6% importancia): Reduce certeza
5. **Sin email** (reduce confianza en el lead)

 IMPORTANTE: El modelo NO sabe que está "En proceso de pago"
   Esa información está en la columna 'Resolución' que fue EXCLUIDA
   para evitar data leakage.

El 44.4% se basa SOLO en:
- Universidad
- Actividad de llamadas  
- Tiempo de gestión
- Categoría de programa
- Datos de contacto

Si el modelo SUPIERA que está "En proceso de pago", 
la probabilidad sería mucho más alta (>80%).
    """)
    
    # Verificar que Resolución NO está en features
    print("\n" + "="*80)
    print(" VERIFICACIÓN DE NO DATA LEAKAGE:")
    print("="*80)
    columnas_leakage = ['Resolución', 'Resolucion', 'Ultima resolución', 'Estado principal', 'Etapa']
    for col in columnas_leakage:
        if col in features_modelo:
            print(f"   {col} - PRESENTE (ERROR!)")
        else:
            print(f"   {col} - EXCLUIDA (correcto)")
    
    print(f"\n Resolución REAL del lead: {lead['Resolución'].values[0]}")
    print(f"   (Esta info NO fue usada por el modelo)")
    
else:
    print("Lead no encontrado en datos procesados")
