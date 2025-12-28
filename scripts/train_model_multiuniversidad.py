"""
Entrenamiento del Modelo Multi-Universidad - Smart Scoring
Entrena un modelo Random Forest global con datos de 5 universidades
"""

import pandas as pd
import numpy as np
import sys
import io
from pathlib import Path
import pickle
import json

# Machine Learning
from sklearn.model_selection import train_test_split, StratifiedKFold
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import (
    classification_report, 
    confusion_matrix, 
    roc_auc_score,
    roc_curve,
    precision_recall_curve,
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

def preparar_datos(df):
    """
    Prepara los datos para el modelo
    """
    print("="*80)
    print("PREPARANDO DATOS PARA EL MODELO GLOBAL")
    print("="*80)
    
    # Separar columnas de ID de features
    columnas_id = ['dcontacto', 'Nombre y Apellido', 'TELTELEFONO', 'EMLMAIL', 'Programa interes']
    
    # Crear copia sin IDs
    df_modelo = df.drop(columns=columnas_id, errors='ignore').copy()
    
    # Separar target
    y = df_modelo['target']
    X = df_modelo.drop(columns=['target'])
    
    print(f"\n📊 Dataset Global: {len(X)} leads")
    print(f"   - Features: {len(X.columns)}")
    print(f"   - Clase 1 (Matriculados): {y.sum()} ({y.mean()*100:.2f}%)")
    print(f"   - Clase 0 (No matriculados): {(y==0).sum()} ({(y==0).mean()*100:.2f}%)")
    
    # Mostrar distribución por universidad
    if 'universidad' in X.columns:
        print(f"\n🎓 Distribución por Universidad:")
        for uni in sorted(X['universidad'].unique()):
            mask = X['universidad'] == uni
            total = mask.sum()
            positivos = y[mask].sum()
            tasa = (positivos / total * 100) if total > 0 else 0
            print(f"   {uni:12s}: {total:6d} leads, {positivos:4d} positivos ({tasa:5.2f}%)")
    
    # Guardar nombres de columnas categoricas
    columnas_categoricas = X.select_dtypes(include=['object']).columns.tolist()
    
    # Codificar variables categoricas
    label_encoders = {}
    
    if columnas_categoricas:
        print(f"\n🔢 Codificando {len(columnas_categoricas)} columnas categóricas...")
        for col in columnas_categoricas:
            le = LabelEncoder()
            X[col] = le.fit_transform(X[col].astype(str))
            label_encoders[col] = le
            print(f"   - {col}: {len(le.classes_)} categorías")
    
    print(f"\n✅ Datos preparados: {X.shape}")
    
    return X, y, label_encoders

def entrenar_modelo(X, y):
    """
    Entrena el modelo Random Forest global
    """
    print("\n" + "="*80)
    print("ENTRENANDO MODELO RANDOM FOREST GLOBAL")
    print("="*80)
    
    # Split train/test
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, 
        test_size=0.2, 
        random_state=42,
        stratify=y
    )
    
    print(f"\n📊 División de datos:")
    print(f"   - Entrenamiento: {len(X_train)} leads ({len(X_train)/len(X)*100:.1f}%)")
    print(f"   - Prueba: {len(X_test)} leads ({len(X_test)/len(X)*100:.1f}%)")
    
    # Entrenar Random Forest
    print("\n🤖 Entrenando Random Forest...")
    
    modelo = RandomForestClassifier(
        n_estimators=100,
        max_depth=10,
        min_samples_split=20,
        min_samples_leaf=10,
        class_weight='balanced',
        random_state=42,
        n_jobs=-1
    )
    
    modelo.fit(X_train, y_train)
    
    print("   ✅ Modelo entrenado exitosamente!")
    
    return modelo, X_train, X_test, y_train, y_test

def evaluar_modelo_global(modelo, X_train, X_test, y_train, y_test, features, df_original):
    """
    Evalúa el modelo globalmente y por universidad
    """
    print("\n" + "="*80)
    print("EVALUANDO MODELO GLOBAL")
    print("="*80)
    
    # Predicciones
    y_pred_test = modelo.predict(X_test)
    y_pred_proba_test = modelo.predict_proba(X_test)[:, 1]
    
    # Métricas globales
    print("\n📊 MÉTRICAS GLOBALES (Test Set):")
    accuracy_test = accuracy_score(y_test, y_pred_test)
    
    try:
        auc_test = roc_auc_score(y_test, y_pred_proba_test)
        print(f"   - Accuracy: {accuracy_test*100:.2f}%")
        print(f"   - AUC-ROC: {auc_test:.4f}")
    except:
        auc_test = 0.0
        print(f"   - Accuracy: {accuracy_test*100:.2f}%")
        print(f"   - AUC-ROC: No calculable (solo una clase en test)")
    
    # Reporte de clasificación
    print("\n📋 Reporte de Clasificación (Test):")
    print(classification_report(y_test, y_pred_test, 
                                target_names=['No Matriculado', 'Matriculado'],
                                zero_division=0))
    
    # Matriz de confusión
    cm = confusion_matrix(y_test, y_pred_test)
    print("\n🔢 Matriz de Confusión:")
    print(f"   TN={cm[0,0]:6d}  |  FP={cm[0,1]:4d}")
    print(f"   FN={cm[1,0]:4d}  |  TP={cm[1,1]:4d}")
    
    # Feature importance
    feature_importance = pd.DataFrame({
        'feature': features,
        'importance': modelo.feature_importances_
    }).sort_values('importance', ascending=False)
    
    print("\n🎯 TOP 10 Features más importantes:")
    print(feature_importance.head(10).to_string(index=False))
    
    # Métricas por universidad
    print("\n" + "="*80)
    print("MÉTRICAS POR UNIVERSIDAD")
    print("="*80)
    
    metricas_por_uni = {}
    
    # Reconstruir índices originales para identificar universidades
    X_test_with_uni = X_test.copy()
    
    if 'universidad' in X_test.columns:
        # Decodificar universidad
        uni_encoder = None
        for feat_name in features:
            if feat_name == 'universidad':
                idx = features.index(feat_name)
                break
        
        universidades_test = X_test['universidad'].values
        
        for uni_code in np.unique(universidades_test):
            mask = universidades_test == uni_code
            if mask.sum() == 0:
                continue
                
            y_uni = y_test[mask]
            y_pred_uni = y_pred_test[mask]
            y_proba_uni = y_pred_proba_test[mask]
            
            # Obtener nombre de universidad
            uni_name = f"Universidad_{uni_code}"
            
            acc_uni = accuracy_score(y_uni, y_pred_uni)
            
            try:
                if y_uni.sum() > 0:
                    auc_uni = roc_auc_score(y_uni, y_proba_uni)
                    recall_uni = recall_score(y_uni, y_pred_uni, zero_division=0)
                    precision_uni = precision_score(y_uni, y_pred_uni, zero_division=0)
                else:
                    auc_uni = 0.0
                    recall_uni = 0.0
                    precision_uni = 0.0
            except:
                auc_uni = 0.0
                recall_uni = 0.0
                precision_uni = 0.0
            
            print(f"\n📍 {uni_name}:")
            print(f"   Leads: {mask.sum()}")
            print(f"   Positivos: {y_uni.sum()}")
            print(f"   Accuracy: {acc_uni*100:.2f}%")
            if auc_uni > 0:
                print(f"   AUC-ROC: {auc_uni:.4f}")
                print(f"   Recall: {recall_uni*100:.2f}%")
                print(f"   Precision: {precision_uni*100:.2f}%")
            
            metricas_por_uni[uni_name] = {
                'total': int(mask.sum()),
                'positivos': int(y_uni.sum()),
                'accuracy': float(acc_uni),
                'auc': float(auc_uni),
                'recall': float(recall_uni),
                'precision': float(precision_uni)
            }
    
    # Métricas para guardar
    metricas = {
        'accuracy_test': float(accuracy_test),
        'auc_test': float(auc_test),
        'n_train': int(len(X_train)),
        'n_test': int(len(X_test)),
        'feature_importance': feature_importance.to_dict('records'),
        'metricas_por_universidad': metricas_por_uni
    }
    
    return metricas, y_pred_proba_test, feature_importance

def crear_visualizaciones(y_test, y_pred_proba, feature_importance, output_dir):
    """
    Crea visualizaciones del modelo
    """
    print("\n" + "="*80)
    print("CREANDO VISUALIZACIONES")
    print("="*80)
    
    # 1. Curva ROC
    print("\n📊 [1/3] Curva ROC...")
    try:
        fpr, tpr, _ = roc_curve(y_test, y_pred_proba)
        auc = roc_auc_score(y_test, y_pred_proba)
        
        plt.figure(figsize=(8, 6))
        plt.plot(fpr, tpr, label=f'ROC Curve (AUC = {auc:.3f})', linewidth=2)
        plt.plot([0, 1], [0, 1], 'k--', label='Random')
        plt.xlabel('False Positive Rate', fontsize=12)
        plt.ylabel('True Positive Rate', fontsize=12)
        plt.title('Curva ROC - Modelo Global Multi-Universidad', fontsize=14, fontweight='bold')
        plt.legend(fontsize=10)
        plt.grid(alpha=0.3)
        plt.tight_layout()
        plt.savefig(output_dir / 'roc_curve.png', dpi=150)
        plt.close()
    except:
        print("   ⚠️ No se pudo crear curva ROC (solo una clase en test)")
    
    # 2. Feature Importance
    print("📊 [2/3] Feature Importance...")
    top_features = feature_importance.head(15)
    
    plt.figure(figsize=(10, 8))
    plt.barh(range(len(top_features)), top_features['importance'], color='steelblue')
    plt.yticks(range(len(top_features)), top_features['feature'])
    plt.xlabel('Importancia', fontsize=12)
    plt.title('Top 15 Features Más Importantes - Modelo Global', fontsize=14, fontweight='bold')
    plt.gca().invert_yaxis()
    plt.grid(axis='x', alpha=0.3)
    plt.tight_layout()
    plt.savefig(output_dir / 'feature_importance.png', dpi=150)
    plt.close()
    
    # 3. Distribución de Scores
    print("📊 [3/3] Distribución de Scores...")
    plt.figure(figsize=(10, 6))
    plt.hist(y_pred_proba[y_test == 0], bins=20, alpha=0.6, label='No Matriculado', color='red')
    plt.hist(y_pred_proba[y_test == 1], bins=20, alpha=0.6, label='Matriculado', color='green')
    plt.xlabel('Probabilidad Predicha', fontsize=12)
    plt.ylabel('Frecuencia', fontsize=12)
    plt.title('Distribución de Scores - Modelo Global', fontsize=14, fontweight='bold')
    plt.legend(fontsize=10)
    plt.grid(alpha=0.3)
    plt.tight_layout()
    plt.savefig(output_dir / 'score_distribution.png', dpi=150)
    plt.close()
    
    print("\n   ✅ Gráficos guardados en carpeta models/")

def guardar_modelo(modelo, label_encoders, metricas, output_dir):
    """
    Guarda el modelo y artifacts
    """
    print("\n" + "="*80)
    print("GUARDANDO MODELO GLOBAL Y ARTIFACTS")
    print("="*80)
    
    # Guardar modelo
    ruta_modelo = output_dir / 'modelo_global_multiuniversidad.pkl'
    with open(ruta_modelo, 'wb') as f:
        pickle.dump(modelo, f)
    print(f"\n💾 Modelo guardado: {ruta_modelo}")
    
    # Guardar encoders
    ruta_encoders = output_dir / 'label_encoders.pkl'
    with open(ruta_encoders, 'wb') as f:
        pickle.dump(label_encoders, f)
    print(f"💾 Encoders guardados: {ruta_encoders}")
    
    # Guardar métricas
    ruta_metricas = output_dir / 'metricas_modelo_global.json'
    with open(ruta_metricas, 'w', encoding='utf-8') as f:
        json.dump(metricas, f, indent=2, ensure_ascii=False)
    print(f"💾 Métricas guardadas: {ruta_metricas}")

if __name__ == "__main__":
    # Rutas
    BASE_DIR = Path(__file__).parent.parent
    RUTA_DATOS = BASE_DIR / "data" / "datos_multi_universidad_features.csv"
    OUTPUT_DIR = BASE_DIR / "models"
    OUTPUT_DIR.mkdir(exist_ok=True)
    
    # Cargar datos
    print("\n📂 Cargando datos multi-universidad con features...")
    df = pd.read_csv(RUTA_DATOS)
    print(f"✅ Cargados {len(df)} leads de {df['universidad'].nunique()} universidades")
    
    # Preparar datos
    X, y, label_encoders = preparar_datos(df)
    
    # Entrenar modelo
    modelo, X_train, X_test, y_train, y_test = entrenar_modelo(X, y)
    
    # Evaluar
    metricas, y_pred_proba, feature_importance = evaluar_modelo_global(
        modelo, X_train, X_test, y_train, y_test, X.columns.tolist(), df
    )
    
    # Visualizaciones
    crear_visualizaciones(y_test, y_pred_proba, feature_importance, OUTPUT_DIR)
    
    # Guardar
    guardar_modelo(modelo, label_encoders, metricas, OUTPUT_DIR)
    
    print("\n" + "="*80)
    print("PROCESO COMPLETADO EXITOSAMENTE")
    print("="*80)
    print(f"\n🎉 MODELO GLOBAL LISTO PARA USAR!")
    print(f"   - Total leads entrenamiento: {len(df):,}")
    print(f"   - Universidades: {df['universidad'].nunique()}")
    if metricas['auc_test'] > 0:
        print(f"   - AUC-ROC en Test: {metricas['auc_test']:.4f}")
    print(f"   - Accuracy en Test: {metricas['accuracy_test']*100:.2f}%")
    print(f"\n📁 Archivos generados en carpeta models/")
