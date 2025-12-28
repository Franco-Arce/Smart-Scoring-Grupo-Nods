"""
Script para Crear/Actualizar Configuración de Normalización
Analiza todos los archivos de universidades y genera normalization_config.json
"""

import pandas as pd
import numpy as np
from pathlib import Path
import json
from collections import defaultdict
import sys
import io

# Configurar encoding UTF-8
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def analizar_columnas_universidades(archivos):
    """Analiza columnas de todas las universidades"""
    print("="*80)
    print("ANÁLISIS DE COLUMNAS POR UNIVERSIDAD")
    print("="*80)
    
    todas_columnas = defaultdict(list)
    
    for nombre, archivo in archivos.items():
        if not archivo.exists():
            print(f"⚠️  {nombre}: Archivo no encontrado")
            continue
            
        df = pd.read_excel(archivo)
        print(f"\n📂 {nombre}: {len(df.columns)} columnas")
        
        for col in df.columns:
            todas_columnas[col].append(nombre)
    
    return todas_columnas

def detectar_variaciones_columnas(todas_columnas):
    """Detecta variaciones de nombres de columnas"""
    print("\n" + "="*80)
    print("DETECCIÓN DE VARIACIONES DE COLUMNAS")
    print("="*80)
    
    mapeos = {}
    
    # Normalizar espacios
    for col in todas_columnas.keys():
        if col != col.strip():
            mapeos[col] = col.strip()
            print(f"✓ Trailing space: '{col}' → '{col.strip()}'")
    
    # Detectar variaciones conocidas
    variaciones = {
        'Resolucion': 'Resolución',
        'Idcontacto': 'dcontacto',
        'Lamadas_discador': 'Llamadas_discador',
        'CHKENTRANTEWHATSAPP': 'WhatsApp entrante',
        'TXTESTADOPRINCIPAL': 'Estado principal',
        'Contador de Llamadas': 'CONTADOR_LLAMADOS_TEL',
        'Fecha Inserción Leads': 'Fecha insert Lead',
        'UTM Origen': 'UTM Source',
        'Ultima resolucion': 'Ultima resolución',
        'Fecha y hora de actualizacion': 'Fecha y hora de actualización',
        'Fecha y hora del proximo llamado': 'Fecha y hora del próximo llamado',
        'TELWHATSAPP': 'WhatsApp',
    }
    
    for origen, destino in variaciones.items():
        if origen in todas_columnas or origen + ' ' in todas_columnas:
            mapeos[origen] = destino
            if origen + ' ' in todas_columnas:
                mapeos[origen + ' '] = destino
            print(f"✓ Mapeo: '{origen}' → '{destino}'")
    
    return mapeos

def analizar_resoluciones(archivos):
    """Analiza todos los valores de Resolución"""
    print("\n" + "="*80)
    print("ANÁLISIS DE VALORES DE RESOLUCIÓN")
    print("="*80)
    
    todas_resoluciones = defaultdict(int)
    
    for nombre, archivo in archivos.items():
        if not archivo.exists():
            continue
            
        df = pd.read_excel(archivo)
        
        # Buscar columna de resolución
        col_res = None
        for col in df.columns:
            if col.strip().lower() in ['resolución', 'resolucion']:
                col_res = col
                break
        
        if col_res:
            valores = df[col_res].value_counts()
            print(f"\n📊 {nombre}: {len(valores)} valores únicos")
            for val, count in valores.head(10).items():
                todas_resoluciones[str(val).strip()] += count
                
    return todas_resoluciones

def categorizar_resoluciones(resoluciones):
    """Categoriza valores de resolución"""
    print("\n" + "="*80)
    print("CATEGORIZACIÓN DE RESOLUCIONES")
    print("="*80)
    
    categorias = {
        'success': [],
        'in_progress': [],
        'rejected_enrolled_elsewhere': [],
        'rejected_no_contact': [],
        'rejected_phone_issue': [],
        'rejected_whatsapp_issue': [],
        'rejected_not_interested': [],
        'rejected_other': [],
        'informational': []
    }
    
    # Palabras clave para categorización
    keywords = {
        'success': ['matriculado', 'admitido', 'inscripto en curso', 'alumno de la universidad'],
        'in_progress': ['proceso de pago', 'oportunidad de venta', 'compromiso pago', 'analizando propuesta'],
        'rejected_enrolled_elsewhere': ['inscripto en otra'],
        'rejected_no_contact': ['no contesta', 'notprocessed', 'noanswer', 'buzon', 'answering', 'unallocated', 
                                'rejected', 'timeout', 'cierre de lead', 'imposible contactar'],
        'rejected_phone_issue': ['telefono erroneo', 'teléfono erróneo', 'fuera de servicio'],
        'rejected_whatsapp_issue': ['deja de responder whatsapp', 'dejo de responder whatsapp', 
                                     'responde mensaje de whastapp'],
        'rejected_not_interested': ['no es la oferta', 'parece caro', 'motivos personales', 'pide no ser llamado',
                                     'spam', 'no cumple requisito', 'horarios', 'modalidad', 'movilidad',
                                     'siguiente cohorte', 'busca maestría'],
        'rejected_other': ['duplicado', 'dejo de responder', 'no indica motivo', 'cerrado por total'],
        'informational': ['se brinda informacion', 'se brinda información', 'plantilla bienvenida', 'volver a llamar']
    }
    
    for resolucion in resoluciones.keys():
        res_lower = resolucion.lower()
        categorizado = False
        
        for categoria, palabras in keywords.items():
            if any(palabra in res_lower for palabra in palabras):
                if resolucion not in categorias[categoria]:
                    categorias[categoria].append(resolucion)
                    print(f"✓ {categoria:30s}: {resolucion}")
                categorizado = True
                break
        
        if not categorizado:
            print(f"⚠️  Sin categoría: {resolucion}")
    
    return categorias

def generar_config(mapeos_columnas, categorias_resoluciones):
    """Genera el archivo de configuración"""
    config = {
        "version": "1.0",
        "description": "Normalization configuration for multi-university data",
        "column_mappings": mapeos_columnas,
        "resolution_mappings": categorias_resoluciones,
        "resolution_to_binary": {
            "success": 1,
            "in_progress": 0,
            "rejected_enrolled_elsewhere": 0,
            "rejected_no_contact": 0,
            "rejected_phone_issue": 0,
            "rejected_whatsapp_issue": 0,
            "rejected_not_interested": 0,
            "rejected_other": 0,
            "informational": 0
        },
        "required_columns": [
            "dcontacto",
            "Resolución",
            "Base de datos",
            "Canal",
            "EMLMAIL",
            "TELTELEFONO"
        ],
        "optional_columns": [
            "CONTADOR_LLAMADOS_TEL",
            "Llamadas_discador",
            "Fecha insert Lead",
            "Fecha y hora de actualización",
            "Fecha y hora del próximo llamado",
            "Nombre y Apellido",
            "Programa interes",
            "WhatsApp entrante",
            "WhatsApp",
            "Estado principal",
            "Etapa",
            "Ultima resolución",
            "UTM Source",
            "UTM Medium",
            "UTM Campaing",
            "UTM Content",
            "UTM TERM",
            "Operador",
            "Nombre Operador",
            "Mensaje"
        ],
        "leakage_columns": [
            "Resolución",
            "Resolucion",
            "Ultima resolución",
            "Ultima resolucion",
            "Estado principal",
            "TXTESTADOPRINCIPAL",
            "Etapa"
        ],
        "data_types": {
            "dcontacto": "int64",
            "CONTADOR_LLAMADOS_TEL": "float64",
            "Llamadas_discador": "float64",
            "TELTELEFONO": "float64",
            "Fecha insert Lead": "datetime64[ns]",
            "Fecha y hora de actualización": "datetime64[ns]",
            "Fecha y hora del próximo llamado": "datetime64[ns]"
        },
        "universities": [
            "UNAB",
            "Crexe",
            "UEES",
            "Anahuac",
            "Unisangil"
        ]
    }
    
    return config

if __name__ == "__main__":
    BASE_DIR = Path(__file__).parent.parent
    DATA_DIR = BASE_DIR / "data"
    CONFIG_DIR = BASE_DIR / "config"
    
    # Crear directorio de config si no existe
    CONFIG_DIR.mkdir(exist_ok=True)
    
    # Archivos de universidades
    archivos = {
        'UNAB': DATA_DIR / 'Consulta_Base_Unificada_UNAB.xls',
        'Crexe': DATA_DIR / 'Reporte_Bases_Unificadas_Crexe.xls',
        'UEES': DATA_DIR / 'Consulta_Base_Unificada_UEES.xls',
        'Anahuac': DATA_DIR / 'Consulta_Base_Unificada_Anahuac.xls',
        'Unisangil': DATA_DIR / 'Consulta_Base_Unificada_Unisangil.xls'
    }
    
    print("\n🚀 GENERADOR DE CONFIGURACIÓN DE NORMALIZACIÓN")
    print("="*80)
    
    # Analizar columnas
    todas_columnas = analizar_columnas_universidades(archivos)
    
    # Detectar variaciones
    mapeos = detectar_variaciones_columnas(todas_columnas)
    
    # Analizar resoluciones
    resoluciones = analizar_resoluciones(archivos)
    
    # Categorizar resoluciones
    categorias = categorizar_resoluciones(resoluciones)
    
    # Generar configuración
    config = generar_config(mapeos, categorias)
    
    # Guardar
    config_path = CONFIG_DIR / 'normalization_config.json'
    with open(config_path, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=2, ensure_ascii=False)
    
    print("\n" + "="*80)
    print(f"✅ Configuración guardada en: {config_path}")
    print("="*80)
    print(f"\n📊 Resumen:")
    print(f"   - Mapeos de columnas: {len(mapeos)}")
    print(f"   - Categorías de resolución: {len(categorias)}")
    print(f"   - Total valores de resolución: {len(resoluciones)}")
    print(f"   - Universidades: {len(archivos)}")
