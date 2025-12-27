import pandas as pd
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Cargar archivo
df = pd.read_excel('data/Reporte_Bases_Unificadas_Crexe.xls')

print("="*80)
print("ANALISIS DE COMPATIBILIDAD - CREXE")
print("="*80)

print(f"\nTotal de leads: {len(df):,}")
print(f"Total de columnas: {len(df.columns)}")

print("\n" + "="*80)
print("1. COMPARACION DE COLUMNAS")
print("="*80)

# Columnas esperadas de UNAB
columnas_unab = [
    'dcontacto', 'Fecha insert Lead', 'Fecha y hora de actualizacion',
    'Nombre y Apellido', 'TELTELEFONO', 'EMLMAIL', 'Base de datos',
    'Ultima resolucion', 'Programa interes', 'Llamadas_discador',
    'WhatsApp entrante', 'CONTADOR_LLAMADOS_TEL', 'Resolucion'
]

# Columnas de Crexe (normalizar espacios)
columnas_crexe_raw = df.columns.tolist()
columnas_crexe = [col.strip() for col in columnas_crexe_raw]

print("\nColumnas en Crexe:")
for i, (raw, clean) in enumerate(zip(columnas_crexe_raw, columnas_crexe), 1):
    if raw != clean:
        print(f"{i:2d}. \"{raw}\" -> \"{clean}\" (tiene espacios)")
    else:
        print(f"{i:2d}. {clean}")

print("\n" + "="*80)
print("2. MAPEO DE COLUMNAS")
print("="*80)

mapeo = {
    'Idcontacto': 'dcontacto',
    'Fecha insert Lead ': 'Fecha insert Lead',
    'Fecha y hora de actualizacion ': 'Fecha y hora de actualizacion',
    'Nombre y Apellido ': 'Nombre y Apellido',
    'Programa interes ': 'Programa interes',
    'Resolucion ': 'Resolucion',
    'Lamadas_discador': 'Llamadas_discador',
    'CHKENTRANTEWHATSAPP': 'WhatsApp entrante (diferente formato)'
}

print("\nMapeo necesario:")
for crexe_col, unab_col in mapeo.items():
    tiene = "SI" if crexe_col in columnas_crexe_raw else "NO"
    print(f"  {tiene} | {crexe_col:35s} -> {unab_col}")

print("\n" + "="*80)
print("3. ANALISIS DE RESOLUCIONES")
print("="*80)

res_col = [c for c in df.columns if 'resoluci' in c.lower() and 'ultima' not in c.lower()]
if res_col:
    print(f"\nTop 15 Resoluciones (columna '{res_col[0]}'):")
    print(df[res_col[0]].value_counts().head(15))
    
    # Detectar matriculados
    resoluciones_texto = df[res_col[0]].astype(str).str.lower()
    matriculados = resoluciones_texto.str.contains('matricula', na=False).sum()
    admitidos = resoluciones_texto.str.contains('admit', na=False).sum()
    en_pago = resoluciones_texto.str.contains('pago', na=False).sum()
    
    print(f"\nDeteccion de positivos:")
    print(f"  - Contiene 'matricula': {matriculados}")
    print(f"  - Contiene 'admit': {admitidos}")
    print(f"  - Contiene 'pago': {en_pago}")

print("\n" + "="*80)
print("4. ANALISIS DE PROGRAMAS")
print("="*80)

prog_col = [c for c in df.columns if 'programa' in c.lower()]
if prog_col:
    print(f"\nTop 10 Programas (columna '{prog_col[0]}'):")
    print(df[prog_col[0]].value_counts().head(10))

print("\n" + "="*80)
print("5. COLUMNAS FALTANTES O DIFERENTES")
print("="*80)

print("\nDiferencias importantes:")
print("  - Canal: Crexe lo tiene, UNAB no")
print("  - WhatsApp: Crexe usa 'CHKENTRANTEWHATSAPP', UNAB usa 'WhatsApp entrante'")
print("  - TXTESTADOPRINCIPAL: Diferente de 'Estado principal'")
print("  - Lamadas_discador: Typo en Crexe (Lamadas vs Llamadas)")

print("\n" + "="*80)
print("CONCLUSION")
print("="*80)
print("\nCompatibilidad: ALTA CON AJUSTES MENORES")
print("Acciones necesarias:")
print("  1. Normalizar nombres de columnas (quitar espacios)")
print("  2. Mapear CHKENTRANTEWHATSAPP -> WhatsApp entrante")
print("  3. Corregir typo Lamadas -> Llamadas")
print("  4. Mapear Idcontacto -> dcontacto")
print("\nEl procesamiento deberia funcionar con ajustes minimos.")
