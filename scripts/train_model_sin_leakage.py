"""
Entrenamiento del Modelo Multi-Universidad SIN DATA LEAKAGE
Entrena un modelo usando SOLO features disponibles al momento del contacto inicial
"""

import pandas as pd
import numpy as np
import sys
import io
from pathlib import Path
import pickle
import json

# Machine Learning
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import (
    classification_report, 
    confusion_matrix, 
    roc_auc_score,
    roc_curve,
    accuracy_score,
    recall_score,
    precision_score
)

# Visualizacion
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns

# Configurar encoding UTF-8
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Configurar estilo de graficos
sns.set_style('whitegrid')
plt.rcParams['figure.figsize'] = (10, 6)

# FEATURES VALIDAS - SIN DATA LEAKAGE
FEATURES_VALIDAS = [
    # Identificador
    'universidad',
    
    # Comportamiento
    'CONTADOR_LLAMADOS_TEL',
    'Llamadas_discador',
    'dias_gestion',
    'ratio_llamadas_dias',
    'alta_actividad_llamadas',
    'lead_reciente',
    'lead_antiguo',
    
    # Contacto
    'tiene_email',
    'whatsapp_entrante_flag',
    
    # Programa
    'programa_categoria',
    'base_categoria',
    
    # Origen
    'utm_source_clean',
    'utm_medium_clean',
]

# COLUMNAS CON LEAKAGE - NO USAR
COLUMNAS_LEAKAGE = [
    'Resolución',
    'Resolucion',
    'Ultima resolución',
    'Ultima resolucion',
    'Estado principal',
]

def preparar_datos_sin_leakage(df):
    """
    Prepara los datos usando SOLO features sin leakage
    """
    print("="*80)
    print("PREPARANDO DATOS SIN DATA LEAKAGE")
    print("="*80)
    
    # Verificar que no usamos columnas con leakage
    columnas_usadas = set(df.columns)
    leakage_detectado = columnas_usadas & set(COLUMNAS_LEAKAGE)
    
    if leakage_detectado:
        print(f"\nADVERTENCIA: Columnas con leakage presentes en dataset:")
        for col in leakage_detectado:
            print(f"   - {col} (sera EXCLUIDA)")
    
    print(f"\nFEATURES VALIDAS A USAR:")
    for i, feat in enumerate(FEATURES_VALIDAS, 1):
        if feat in df.columns:
            print(f"   {i:2d}. {feat}")
    
    # Separar target
    y = df['target']
    
    # Seleccionar SOLO features validas
    X = df[FEATURES_VALIDAS].copy()
    
    print(f"\nDATASET PREPARADO:")
    print(f"   Total leads: {len(X):,}")
    print(f"   Features: {len(X.columns)}")
    print(f"   Positivos: {y.sum():,} ({y.mean()*100:.2f}%)")
    print(f"   Negativos: {(y==0).sum():,} ({(y==0).mean()*100:.2f}%)")
    
    # Distribucion por universidad
    if 'universidad' in X.columns:
        print(f"\nDISTRIBUCION POR UNIVERSIDAD:")
        for uni in sorted(X['universidad'].unique()):
            mask = X['universidad'] == uni
            total = mask.sum()
            positivos = y[mask].sum()
            tasa = (positivos / total * 100) if total > 0 else 0
            print(f"   {uni:12s}: {total:6,} leads | {positivos:4.0f} positivos | {tasa:5.2f}%")
    
    # Codificar variables categoricas
    columnas_categoricas = X.select_dtypes(include=['object']).columns.tolist()
    label_encoders = {}
    
    if columnas_categoricas:
        print(f"\nCODIFICANDO FEATURES CATEGORICAS:")
        for col in columnas_categoricas:
            le = LabelEncoder()
            X[col] = le.fit_transform(X[col].astype(str))
            label_encoders[col] = le
            print(f"   - {col}: {len(le.classes_)} categorias")
    
    return X, y, label_encoders

def entrenar_modelo_limpio(X, y):
    """
    Entrena modelo Random Forest con features limpias
    """
    print("\n" + "="*80)
    print("ENTRENANDO MODELO SIN DATA LEAKAGE")
    print("="*80)
    
    # Split train/test (stratified)
    X_train, X_test, y_train, y_test = train_test_split(
        X, y,
        test_size=0.2,
        random_state=42,
        stratify=y
    )
    
    print(f"\nDIVISION DE DATOS:")
    print(f"   Train: {len(X_train):,} leads ({y_train.sum()} positivos)")
    print(f"   Test:  {len(X_test):,} leads ({y_test.sum()} positivos)")
    
    # Entrenar Random Forest
    print("\nENTRENANDO RANDOM FOREST...")
    
    modelo = RandomForestClassifier(
        n_estimators=100,
        max_depth=10,
        min_samples_split=20,
        min_samples_leaf=10,
        class_weight='balanced',  # Balancea clases desbalanceadas
        random_state=42,
        n_jobs=-1
    )
    
    modelo.fit(X_train, y_train)
    
    print("   -> Modelo entrenado exitosamente!")
    
    return modelo, X_train, X_test, y_train, y_test

def evaluar_modelo_limpio(modelo, X_train, X_test, y_train, y_test, features, df_original):
    """
    Evalua modelo sin leakage
    """
    print("\n" + "="*80)
    print("EVALUACION - MODELO SIN LEAKAGE")
    print("="*80)
    
    # Predicciones
    y_pred_test = modelo.predict(X_test)
    y_pred_proba_test = modelo.predict_proba(X_test)[:, 1]
    
    # Metricas globales
    print("\nMETRICAS GLOBALES (Test Set):")
    accuracy = accuracy_score(y_test, y_pred_test)
    
    try:
        auc = roc_auc_score(y_test, y_pred_proba_test)
        recall = recall_score(y_test, y_pred_test, zero_division=0)
        precision = precision_score(y_test, y_pred_test, zero_division=0)
        
        print(f"   AUC-ROC:   {auc:.4f}")
        print(f"   Accuracy:  {accuracy*100:.2f}%")
        print(f"   Recall:    {recall*100:.2f}%")
        print(f"   Precision: {precision*100:.2f}%")
    except Exception as e:
        auc = 0
        recall = 0
        precision = 0
        print(f"   Accuracy: {accuracy*100:.2f}%")
        print(f"   Advertencia: {str(e)}")
    
    # Matriz de confusion
    cm = confusion_matrix(y_test, y_pred_test)
    print("\nMATRIZ DE CONFUSION:")
    print(f"   TN={cm[0,0]:6d}  |  FP={cm[0,1]:4d}")
    print(f"   FN={cm[1,0]:4d}  |  TP={cm[1,1]:4d}")
    
    # Feature importance
    feature_importance = pd.DataFrame({
        'feature': features,
        'importance': modelo.feature_importances_
    }).sort_values('importance', ascending=False)
    
    print("\nTOP 10 FEATURES MAS IMPORTANTES:")
    print(feature_importance.head(10).to_string(index=False))
    
    # Metricas por universidad
    print("\n" + "="*80)
    print("METRICAS POR UNIVERSIDAD")
    print("="*80)
    
    metricas_por_uni = {}
    X_test_with_uni = X_test.copy()
    
    if 'universidad' in X_test.columns:
        universidades_test = X_test['universidad'].values
        
        for uni_code in np.unique(universidades_test):
            mask = universidades_test == uni_code
            if mask.sum() == 0:
                continue
            
            y_uni = y_test[mask]
            y_pred_uni = y_pred_test[mask]
            y_proba_uni = y_pred_proba_test[mask]
            
            uni_name = f"Universidad_{uni_code}"
            acc_uni = accuracy_score(y_uni, y_pred_uni)
            
            try:
                if y_uni.sum() > 0:
                    auc_uni = roc_auc_score(y_uni, y_proba_uni)
                    recall_uni = recall_score(y_uni, y_pred_uni, zero_division=0)
                    prec_uni = precision_score(y_uni, y_pred_uni, zero_division=0)
                else:
                    auc_uni = 0
                    recall_uni = 0
                    prec_uni = 0
            except:
                auc_uni = 0
                recall_uni = 0
                prec_uni = 0
            
            print(f"\n{uni_name}:")
            print(f"   Leads: {mask.sum():,} | Positivos: {y_uni.sum()}")
            print(f"   Accuracy: {acc_uni*100:.2f}%", end="")
            if auc_uni > 0:
                print(f" | AUC: {auc_uni:.4f} | Recall: {recall_uni*100:.1f}% | Prec: {prec_uni*100:.1f}%")
            else:
                print()
            
            metricas_por_uni[uni_name] = {
                'total': int(mask.sum()),
                'positivos': int(y_uni.sum()),
                'accuracy': float(acc_uni),
                'auc': float(auc_uni),
                'recall': float(recall_uni),
                'precision': float(prec_uni)
            }
    
    # Metricas para guardar
    metricas = {
        'accuracy_test': float(accuracy),
        'auc_test': float(auc),
        'recall_test': float(recall),
        'precision_test': float(precision),
        'n_train': int(len(X_train)),
        'n_test': int(len(X_test)),
        'sin_leakage': True,
        'features_usadas': FEATURES_VALIDAS,
        'feature_importance': feature_importance.to_dict('records'),
        'metricas_por_universidad': metricas_por_uni
    }
    
    return metricas, y_pred_proba_test, feature_importance

def crear_visualizaciones(y_test, y_pred_proba, feature_importance, output_dir):
    """Crea visualizaciones del modelo"""
    print("\n" + "="*80)
    print("CREANDO VISUALIZACIONES")
    print("="*80)
    
    # 1. Curva ROC
    print("\n[1/3] Curva ROC...")
    try:
        fpr, tpr, _ = roc_curve(y_test, y_pred_proba)
        auc = roc_auc_score(y_test, y_pred_proba)
        
        plt.figure(figsize=(8, 6))
        plt.plot(fpr, tpr, label=f'ROC Curve (AUC = {auc:.3f})', linewidth=2)
        plt.plot([0, 1], [0, 1], 'k--', label='Random')
        plt.xlabel('False Positive Rate', fontsize=12)
        plt.ylabel('True Positive Rate', fontsize=12)
        plt.title('Curva ROC - Modelo SIN Leakage', fontsize=14, fontweight='bold')
        plt.legend(fontsize=10)
        plt.grid(alpha=0.3)
        plt.tight_layout()
        plt.savefig(output_dir / 'roc_curve_sin_leakage.png', dpi=150)
        plt.close()
    except Exception as e:
        print(f"   Advertencia: {str(e)}")
    
    # 2. Feature Importance
    print("[2/3] Feature Importance...")
    top_features = feature_importance.head(14)  # Todas las features
    
    plt.figure(figsize=(10, 8))
    plt.barh(range(len(top_features)), top_features['importance'], color='steelblue')
    plt.yticks(range(len(top_features)), top_features['feature'])
    plt.xlabel('Importancia', fontsize=12)
    plt.title('Features Validadas (Sin Leakage)', fontsize=14, fontweight='bold')
    plt.gca().invert_yaxis()
    plt.grid(axis='x', alpha=0.3)
    plt.tight_layout()
    plt.savefig(output_dir / 'feature_importance_sin_leakage.png', dpi=150)
    plt.close()
    
    # 3. Distribucion de Scores
    print("[3/3] Distribucion de Scores...")
    plt.figure(figsize=(10, 6))
    plt.hist(y_pred_proba[y_test == 0], bins=20, alpha=0.6, label='No Matriculado', color='red')
    plt.hist(y_pred_proba[y_test == 1], bins=20, alpha=0.6, label='Matriculado', color='green')
    plt.xlabel('Probabilidad Predicha', fontsize=12)
    plt.ylabel('Frecuencia', fontsize=12)
    plt.title('Distribucion de Scores - Modelo Sin Leakage', fontsize=14, fontweight='bold')
    plt.legend(fontsize=10)
    plt.grid(alpha=0.3)
    plt.tight_layout()
    plt.savefig(output_dir / 'score_distribution_sin_leakage.png', dpi=150)
    plt.close()
    
    print("\n   -> Graficos guardados!")

def guardar_modelo(modelo, label_encoders, metricas, output_dir):
    """Guarda el modelo y artifacts"""
    print("\n" + "="*80)
    print("GUARDANDO MODELO SIN LEAKAGE")
    print("="*80)
    
    # Guardar modelo
    ruta_modelo = output_dir / 'modelo_scoring_sin_leakage.pkl'
    with open(ruta_modelo, 'wb') as f:
        pickle.dump(modelo, f)
    print(f"\n   Modelo guardado: {ruta_modelo}")
    
    # Guardar encoders
    ruta_encoders = output_dir / 'label_encoders_sin_leakage.pkl'
    with open(ruta_encoders, 'wb') as f:
        pickle.dump(label_encoders, f)
    print(f"   Encoders guardados: {ruta_encoders}")
    
    # Guardar metricas
    ruta_metricas = output_dir / 'metricas_modelo_sin_leakage.json'
    with open(ruta_metricas, 'w', encoding='utf-8') as f:
        json.dump(metricas, f, indent=2, ensure_ascii=False)
    print(f"   Metricas guardadas: {ruta_metricas}")

if __name__ == "__main__":
    # Rutas
    BASE_DIR = Path(__file__).parent.parent
    RUTA_DATOS = BASE_DIR / "data" / "datos_multi_universidad_features.csv"
    OUTPUT_DIR = BASE_DIR / "models"
    OUTPUT_DIR.mkdir(exist_ok=True)
    
    # Cargar datos
    print("\nCargando datos multi-universidad...")
    df = pd.read_csv(RUTA_DATOS, low_memory=False)
    print(f"Cargados {len(df):,} leads")
    
    # Preparar datos SIN leakage
    X, y, label_encoders = preparar_datos_sin_leakage(df)
    
    # Entrenar modelo
    modelo, X_train, X_test, y_train, y_test = entrenar_modelo_limpio(X, y)
    
    # Evaluar
    metricas, y_pred_proba, feature_importance = evaluar_modelo_limpio(
        modelo, X_train, X_test, y_train, y_test, X.columns.tolist(), df
    )
    
    # Visualizaciones
    crear_visualizaciones(y_test, y_pred_proba, feature_importance, OUTPUT_DIR)
    
    # Guardar
    guardar_modelo(modelo, label_encoders, metricas, OUTPUT_DIR)
    
    print("\n" + "="*80)
    print("PROCESO COMPLETADO - MODELO SIN LEAKAGE LISTO")
    print("="*80)
    print(f"\nMODELO PRODUCCION-READY:")
    print(f"   Total leads entrenamiento: {len(df):,}")
    print(f"   Features validas: {len(FEATURES_VALIDAS)}")
    if metricas['auc_test'] > 0:
        print(f"   AUC-ROC: {metricas['auc_test']:.4f}")
    print(f"   Accuracy: {metricas['accuracy_test']*100:.2f}%")
    print(f"   Sin data leakage: SI")
    print(f"\nArchivos en models/")
