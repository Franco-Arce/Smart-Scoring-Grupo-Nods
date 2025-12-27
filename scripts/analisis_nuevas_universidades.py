"""
Análisis rápido de todas las nuevas universidades
"""
import pandas as pd
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

universidades = [
    ('Anahuac', 'data/Consulta_Base_Unificada_Anahuac.xls'),
    ('Unisangil', 'data/Consulta_Base_Unificada_Unisangil.xls')
]

print("="*80)
print("ANALISIS RAPIDO - NUEVAS UNIVERSIDADES")
print("="*80)

for nombre, archivo in universidades:
    try:
        df = pd.read_excel(archivo)
        
        print(f"\n{'='*80}")
        print(f"{nombre.upper()}")
        print(f"{'='*80}")
        
        print(f"\nTotal leads: {len(df):,}")
        print(f"Columnas: {len(df.columns)}")
        
        # Columnas
        print(f"\nColumnas detectadas:")
        columnas_clean = [col.strip() for col in df.columns]
        for i, col in enumerate(columnas_clean[:10], 1):
            print(f"  {i:2d}. {col}")
        if len(df.columns) > 10:
            print(f"  ... y {len(df.columns) - 10} más")
        
        # Verificar columnas críticas
        criticas = {
            'id': any('dcontacto' in c.lower() or 'idcontacto' in c.lower() for c in columnas_clean),
            'nombre': any('nombre' in c.lower() for c in columnas_clean),
            'telefono': any('telefono' in c.lower() for c in columnas_clean),
            'email': any('mail' in c.lower() for c in columnas_clean),
            'resolucion': any('resoluci' in c.lower() for c in columnas_clean),
            'programa': any('programa' in c.lower() for c in columnas_clean)
        }
        
        print(f"\nColumnas críticas encontradas:")
        for col, encontrada in criticas.items():
            status = "✓" if encontrada else "✗"
            print(f"  {status} {col}")
        
        # Resoluciones
        res_cols = [c for c in df.columns if 'resoluci' in c.lower() and 'ultima' not in c.lower()]
        if res_cols:
            print(f"\nTop 10 Resoluciones:")
            print(df[res_cols[0]].value_counts().head(10))
            
            # Contar positivos
            res_lower = df[res_cols[0]].astype(str).str.lower()
            matriculados = res_lower.str.contains('matricula', na=False).sum()
            admitidos = res_lower.str.contains('admit', na=False).sum()
            en_pago = res_lower.str.contains('pago', na=False).sum()
            total_positivos = matriculados + admitidos + en_pago
            
            print(f"\nPositivos detectados:")
            print(f"  Matriculados: {matriculados}")
            print(f"  Admitidos: {admitidos}")
            print(f"  En pago: {en_pago}")
            print(f"  TOTAL: {total_positivos} ({total_positivos/len(df)*100:.2f}%)")
        
        # Compatibilidad
        criticas_count = sum(criticas.values())
        if criticas_count >= 5:
            print(f"\n✅ COMPATIBLE ({criticas_count}/6 columnas críticas)")
        else:
            print(f"\n⚠️ REVISAR ({criticas_count}/6 columnas críticas)")
            
    except Exception as e:
        print(f"\n❌ Error al procesar {nombre}: {str(e)}")

print("\n" + "="*80)
print("RESUMEN DE COMPATIBILIDAD")
print("="*80)
print("\nTodas las universidades procesadas.")
print("Ver detalles arriba para cada institución.")
