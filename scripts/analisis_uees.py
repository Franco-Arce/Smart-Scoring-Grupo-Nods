import pandas as pd
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Cargar archivo
df = pd.read_excel('data/Consulta_Base_Unificada_UEES.xls')

print("="*80)
print("ANALISIS DE COMPATIBILIDAD - UEES")
print("="*80)

print(f"\nTotal de leads: {len(df):,}")
print(f"Total de columnas: {len(df.columns)}")

print("\n" + "="*80)
print("COLUMNAS DETECTADAS")
print("="*80)

columnas_raw = df.columns.tolist()
columnas_clean = [col.strip() for col in columnas_raw]

for i, (raw, clean) in enumerate(zip(columnas_raw, columnas_clean), 1):
    if raw != clean:
        print(f"{i:2d}. \"{raw}\" -> \"{clean}\" (tiene espacios)")
    else:
        print(f"{i:2d}. {clean}")

print("\n" + "="*80)
print("COMPARACION CON FORMATO ESTANDAR")
print("="*80)

# Columnas esperadas (UNAB estandar)
columnas_esperadas = [
    'dcontacto', 'Fecha insert Lead', 'Nombre y Apellido', 
    'TELTELEFONO', 'EMLMAIL', 'Base de datos',
    'Ultima resolución', 'Programa interes', 'Llamadas_discador',
    'WhatsApp entrante', 'CONTADOR_LLAMADOS_TEL', 
    'Fecha y hora de actualización', 'Resolución'
]

print("\nColumnas importantes:")
for col_esperada in columnas_esperadas:
    # Buscar columna (ignorar espacios y acentos)
    encontrada = None
    for col in columnas_clean:
        if col.lower().replace(' ', '') == col_esperada.lower().replace(' ', ''):
            encontrada = col
            break
    
    if encontrada:
        print(f"  ✓ {col_esperada:35s} -> Encontrada como '{encontrada}'")
    else:
        # Buscar parcialmente
        for col in columnas_clean:
            if col_esperada.split()[0].lower() in col.lower():
                print(f"  ~ {col_esperada:35s} -> Similar: '{col}'")
                encontrada = col
                break
        if not encontrada:
            print(f"  ✗ {col_esperada:35s} -> NO ENCONTRADA")

print("\n" + "="*80)
print("ANALISIS DE RESOLUCIONES")
print("="*80)

# Buscar columna de resolución
res_cols = [c for c in df.columns if 'resoluci' in c.lower() and 'ultima' not in c.lower()]
if res_cols:
    print(f"\nColumna de resolución: '{res_cols[0]}'")
    print(f"\nTop 15 resoluciones:")
    print(df[res_cols[0]].value_counts().head(15))
    
    # Buscar matriculados
    res_lower = df[res_cols[0]].astype(str).str.lower()
    matriculados = res_lower.str.contains('matricula', na=False).sum()
    admitidos = res_lower.str.contains('admit', na=False).sum()
    en_pago = res_lower.str.contains('pago', na=False).sum()
    
    print(f"\nPositivos detectados:")
    print(f"  Matriculados: {matriculados}")
    print(f"  Admitidos: {admitidos}")
    print(f"  En pago: {en_pago}")
    print(f"  TOTAL: {matriculados + admitidos + en_pago}")
else:
    print("  ✗ No se encontró columna de Resolución")

print("\n" + "="*80)
print("PRIMERA FILA DE EJEMPLO")
print("="*80)
print(df.head(1).T)

print("\n" + "="*80)
print("CONCLUSION")
print("="*80)

# Columnas críticas
criticas_encontradas = sum([
    any('dcontacto' in c.lower() or 'idcontacto' in c.lower() for c in columnas_clean),
    any('nombre' in c.lower() for c in columnas_clean),
    any('telefono' in c.lower() for c in columnas_clean),
    any('resoluci' in c.lower() for c in columnas_clean),
    any('programa' in c.lower() for c in columnas_clean)
])

if criticas_encontradas >= 4:
    print("\n✅ COMPATIBLE - Columnas esenciales encontradas")
    print("La app debería funcionar con ajustes mínimos en normalización")
else:
    print("\n⚠️ REVISAR - Faltan algunas columnas críticas")
    print("Puede requerir ajustes adicionales en el mapeo")

print(f"\nColumnas críticas encontradas: {criticas_encontradas}/5")
