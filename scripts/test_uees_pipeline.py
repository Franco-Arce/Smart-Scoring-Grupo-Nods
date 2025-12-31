import sys
import os
import pandas as pd
import numpy as np

# AÃ±adir directorio padre al path para importar app
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import detectar_universidad, limpiar_datos_integrado, crear_features_integrado

def test_uees_pipeline():
    file_path = r'C:\Users\franc\OneDrive\Escritorio\Mis Cosas\Prob Leads - Data Science Nods\data\Consulta_Base_Unificada_UEES.xls'
    
    print(f"Cargando archivo: {file_path}")
    try:
        df = pd.read_excel(file_path)
        print(f"Archivo cargado. Dimensiones: {df.shape}")
        print("Columnas originales:", df.columns.tolist()[:10], "...")
    except Exception as e:
        print(f"Error cargando archivo: {e}")
        return

    print("\n--- TEST: DETECCION UNIVERSIDAD ---")
    univ = detectar_universidad(df)
    print(f"Universidad detectada: {univ}")
    if univ != 'UEES':
        print("ALERTA: Universidad incorrecta. Se esperaba UEES.")

    print("\n--- TEST: LIMPIEZA DATOS ---")
    try:
        # Mocking streamlit spinner/success/info since they don't work in script
        import streamlit as st
        
        class MockSpinner:
            def __init__(self, text): pass
            def __enter__(self): pass
            def __exit__(self, exc_type, exc_val, exc_tb): pass

        def safe_print(*args, **kwargs):
            try:
                print(*args, **kwargs)
            except UnicodeEncodeError:
                # Fallback for Windows console issues
                clean_args = []
                for arg in args:
                    if isinstance(arg, str):
                        clean_args.append(arg.encode('ascii', 'replace').decode('ascii'))
                    else:
                        clean_args.append(arg)
                print(*clean_args, **kwargs)

        st.spinner = MockSpinner
        st.info = safe_print
        st.success = safe_print
        st.warning = safe_print
        
        df_limpio = limpiar_datos_integrado(df)
        print(f"Datos limpios: {df_limpio.shape}")
        
        if 'target' in df_limpio.columns:
            print(f"Target distribution:\n{df_limpio['target'].value_counts(normalize=True)}")
        else:
            print("ALERTA: Columna 'target' no creada.")

    except Exception as e:
        print(f"Error en limpieza: {e}")
        import traceback
        traceback.print_exc()
        return

    print("\n--- TEST: FEATURE ENGINEERING ---")
    try:
        st.session_state = {} # Mock session state
        df_features = crear_features_integrado(df_limpio)
        print(f"Features creadas: {df_features.shape}")
        print("Columnas de features:", df_features.columns.tolist())
        
        # Check specific expected columns logic
        if 'universidad' in df_features.columns:
             print(f"Universidad en features: {df_features['universidad'].unique()}")
        
    except Exception as e:
         print(f"Error en features: {e}")
         import traceback
         traceback.print_exc()

if __name__ == "__main__":
    test_uees_pipeline()
