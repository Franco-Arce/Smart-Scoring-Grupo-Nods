
import pandas as pd
import sys
import io
import os
from pathlib import Path

# Configurar encoding UTF-8
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def audit_universities(data_dir):
    """
    Audits all .xls files in the data directory to find status columns and values.
    """
    print("="*80)
    print("AUDITORÍA DE ESTADOS Y RESOLUCIONES - MULTI UNIVERSIDAD")
    print("="*80)
    
    data_path = Path(data_dir)
    files = list(data_path.glob("*.xls"))
    
    uni_data = []

    for file_path in files:
        if "Consulta_Base_Unificada" not in file_path.name and "Reporte_Bases" not in file_path.name:
            continue
            
        print(f"\n📂 Analizando archivo: {file_path.name}")
        try:
            df = pd.read_excel(file_path)
            print(f"   -> Filas: {len(df):,}")
            
            # 1. Buscar columna de Resolución/Estado
            cols = [c.strip() for c in df.columns]
            df.columns = cols  # Normalize column names in DF
            
            target_col = None
            possible_names = ['Resolución', 'Resolucion', 'Ultima resolución', 'Ultima resolucion', 'Estado', 'Status', 'TXTESTADOPRINCIPAL']
            
            for name in possible_names:
                if name in cols:
                    target_col = name
                    break
            
            # Si no encuentra exacto, buscar parcial
            if not target_col:
                for col in cols:
                    if 'resolu' in col.lower() or 'estado' in col.lower():
                        target_col = col
                        break
            
            if target_col:
                print(f"   ✅ Columna Objetivo detectada: '{target_col}'")
                
                # 2. Analizar valores únicos (Top 20)
                print(f"   📊 Top 20 Estados más frecuentes:")
                top_values = df[target_col].value_counts().head(20)
                for val, count in top_values.items():
                    print(f"      - {val}: {count}")
                
                # 3. Detectar posibles éxitos
                possible_success = []
                unique_values = df[target_col].dropna().unique()
                keywords = ['matricula', 'inscri', 'admit', 'pago', 'venta', 'ganada', 'alumno']
                
                for val in unique_values:
                    val_str = str(val).lower()
                    if any(k in val_str for k in keywords):
                        possible_success.append(val)
                
                print(f"   ✨ Posibles Éxitos detectados (contienen keyword):")
                if possible_success:
                    for val in possible_success:
                        print(f"      - {val}")
                else:
                    print("      (Ninguno obvio detectado)")
                    
            else:
                print("   ❌ NO SE ENCONTRÓ COLUMNA DE RESOLUCIÓN/ESTADO")
                print(f"   Columnas disponibles: {cols[:10]}...")

            # 4. Chequear features críticas
            critical_keywords = {
                'Email': ['mail', 'correo'],
                'Phone': ['tel', 'cel', 'movil', 'fono'],
                'Date': ['fecha', 'date']
            }
            
            missing_features = []
            for feature, kws in critical_keywords.items():
                found = False
                for col in cols:
                    if any(kw in col.lower() for kw in kws):
                        found = True
                        break
                if not found:
                    missing_features.append(feature)
            
            if missing_features:
                print(f"   ⚠️ Faltan columnas probables para: {', '.join(missing_features)}")
            else:
                print(f"   ✅ Features básicas detectadas (Email, Teléfono, Fechas)")

        except Exception as e:
            print(f"   ❌ Error leyendo archivo: {str(e)}")

if __name__ == "__main__":
    BASE_DIR = Path(__file__).parent.parent
    DATA_DIR = BASE_DIR / "data"
    
    # Redirect stdout to file
    output_file = BASE_DIR / "audit_report.txt"
    with open(output_file, "w", encoding="utf-8") as f:
        # Redirect sys.stdout
        original_stdout = sys.stdout
        sys.stdout = f
        
        try:
            audit_universities(DATA_DIR)
        finally:
            sys.stdout = original_stdout
            
    print(f"Reporte guardado en: {output_file}")
