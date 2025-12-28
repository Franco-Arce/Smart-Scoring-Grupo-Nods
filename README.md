# Smart Scoring - Sistema de Normalización Multi-Universidad

Sistema automatizado de normalización y scoring de leads para múltiples universidades del Grupo Nods.

## 🎯 Características Principales

- ✅ **Normalización automática** de datos de 5 universidades
- ✅ **133,209 leads** procesados con score de calidad 100/100
- ✅ **42 features** de Machine Learning
- ✅ **Validación automática** de consistencia
- ✅ **Documentación completa** y scripts reutilizables

## 📊 Universidades Soportadas

| Universidad | Leads | Tasa Conversión | Estado |
|-------------|-------|-----------------|--------|
| UNAB | 57,707 | 2.01% | ✅ |
| Crexe | 31,807 | 0.32% | ✅ |
| UEES | 25,767 | 0.80% | ✅ |
| Anahuac | 13,663 | 1.67% | ✅ |
| Unisangil | 4,265 | 0.33% | ✅ |

## 🚀 Inicio Rápido

### Requisitos

```bash
Python 3.8+
pandas
numpy
scikit-learn
streamlit
openpyxl
```

### Instalación

```bash
# Clonar repositorio
git clone https://github.com/TU_USUARIO/Smart-Scoring-Grupo-Nods.git
cd Smart-Scoring-Grupo-Nods

# Instalar dependencias
pip install -r requirements.txt
```

### Uso

#### 1. Normalizar Datos

```bash
# Procesar datos de todas las universidades
python scripts/prepare_multi_university_data.py
```

**Salida:**
- `data/datos_multi_universidad_limpios.csv` - Datos normalizados
- `data/datos_multi_universidad_features.csv` - Con features ML

#### 2. Validar Normalización

```bash
# Validación completa
python scripts/validate_normalization.py --check-resolutions --check-quality
```

#### 3. Auditoría de Calidad

```bash
# Verificar realismo y consistencia
python scripts/audit_final.py
```

#### 4. Ejecutar Aplicación Streamlit

```bash
streamlit run app.py
```

## 📁 Estructura del Proyecto

```
Smart-Scoring-Grupo-Nods/
├── config/
│   └── normalization_config.json    # Configuración de normalización
├── data/
│   ├── README.md                    # Instrucciones para datos
│   └── *.csv                        # Datos procesados (no en Git)
├── docs/
│   └── NORMALIZATION_GUIDE.md       # Guía completa de normalización
├── models/
│   ├── modelo_scoring_sin_leakage.pkl
│   └── *.png                        # Visualizaciones
├── scripts/
│   ├── prepare_multi_university_data.py  # Normalización principal
│   ├── validate_normalization.py         # Validación
│   ├── audit_final.py                    # Auditoría de calidad
│   ├── create_normalization_config.py    # Generador de config
│   └── ...                               # Otros scripts
├── app.py                           # Aplicación Streamlit
├── requirements.txt                 # Dependencias
└── README.md                        # Este archivo
```

## 🔧 Normalización de Datos

### Nombres de Columnas

El sistema normaliza automáticamente **17 variaciones** de nombres de columnas:

| Original | Normalizado | Universidades |
|----------|-------------|---------------|
| `Resolucion` | `Resolución` | Crexe, UEES, Anahuac |
| `Lamadas_discador` | `Llamadas_discador` | Crexe, UEES, Anahuac |
| `CHKENTRANTEWHATSAPP` | `WhatsApp entrante` | Crexe, UEES, Anahuac |
| `Contador de Llamadas` | `CONTADOR_LLAMADOS_TEL` | UEES |

### Valores de Resolución

Categoriza **60+ variaciones** en 9 categorías estándar:

- **Success** (1.28%): Matriculado, Admitido, etc.
- **In Progress** (0.21%): En proceso de pago, Oportunidad de venta
- **Rejected** (94.5%): No contact, Not interested, Phone issue, etc.

### Valores Dentro de Columnas

- **Canal**: `"wsp"`, `"WSP"`, `"Wsp"` → `"whatsapp"`
- **Programa**: Todo a MAYÚSCULAS
- **UTMs**: Todo a minúsculas

## 📈 Calidad de Datos

### Métricas de Completitud

| Campo | Cobertura |
|-------|-----------|
| Teléfono | 99.8% |
| Email válido | 95.8% |
| Programa | 72.9% |
| Resolución | 100% |

### Validación

- ✅ **0 errores críticos**
- ✅ **0 advertencias**
- ✅ **Score: 100/100**

## 🔍 Agregar Nueva Universidad

### Paso 1: Colocar Archivo

```bash
data/Consulta_Base_Unificada_NuevaUniversidad.xls
```

### Paso 2: Analizar Diferencias

```bash
python scripts/analizar_diferencias_universidades.py
```

### Paso 3: Actualizar Configuración

Editar `config/normalization_config.json`:

```json
{
  "column_mappings": {
    "NombreEspecifico": "NombreEstandar"
  },
  "universities": [..., "NuevaUniversidad"]
}
```

### Paso 4: Procesar

```bash
python scripts/prepare_multi_university_data.py
python scripts/validate_normalization.py
```

## 📚 Documentación

- **[Guía de Normalización](docs/NORMALIZATION_GUIDE.md)** - Documentación completa (400+ líneas)
- **[README de Datos](data/README.md)** - Instrucciones para datos

## 🛠️ Scripts Disponibles

| Script | Descripción |
|--------|-------------|
| `prepare_multi_university_data.py` | Normalización principal |
| `validate_normalization.py` | Validación de consistencia |
| `audit_final.py` | Auditoría de calidad |
| `create_normalization_config.py` | Generador de configuración |
| `analizar_diferencias_universidades.py` | Análisis de diferencias |
| `train_model_sin_leakage.py` | Entrenamiento sin data leakage |

## 🎨 Aplicación Streamlit

La aplicación permite:

- 📤 Subir archivos CRM de cualquier universidad
- 🔄 Normalización automática
- 📊 Scoring predictivo de leads
- 📈 Visualizaciones interactivas
- 📥 Exportación de resultados

## ⚠️ Datos Sensibles

**IMPORTANTE**: Los archivos de datos CRM (`.xls`, `.xlsx`, `.csv`) están excluidos del repositorio por contener información sensible.

Para usar el sistema:
1. Coloca tus archivos en la carpeta `data/`
2. Los archivos serán ignorados por Git automáticamente
3. Ejecuta los scripts de normalización

## 📊 Resultados

### Antes de la Normalización

- 43 columnas únicas entre universidades
- Solo 4 columnas comunes
- Datos inconsistentes
- Imposible entrenar modelo global

### Después de la Normalización

- ✅ 32 columnas idénticas en todas
- ✅ 133,209 leads procesados
- ✅ 42 features de ML
- ✅ Score de calidad: 100/100
- ✅ Listo para modelo global

## 🤝 Contribuir

1. Fork el proyecto
2. Crea una rama (`git checkout -b feature/AmazingFeature`)
3. Commit cambios (`git commit -m 'Add AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## 📝 Licencia

Este proyecto es privado y confidencial del Grupo Nods.

## 👥 Contacto

Para consultas técnicas, revisar:
- `docs/NORMALIZATION_GUIDE.md`
- Ejecutar `python scripts/validate_normalization.py`

---

**Desarrollado para**: Grupo Nods  
**Fecha**: Diciembre 2025  
**Estado**: ✅ Producción
