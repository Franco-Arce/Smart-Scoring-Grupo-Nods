# 🎓 Smart Scoring UNAB - Sistema de Lead Scoring Predictivo

![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)
![ML](https://img.shields.io/badge/ML-Random%20Forest-green.svg)
![Streamlit](https://img.shields.io/badge/Streamlit-Public%20App-red.svg)
![Status](https://img.shields.io/badge/Status-Production%20Ready-success.svg)

> 🌐 **Demo Pública**: [https://smart-scoring-nods.streamlit.app](https://smart-scoring-nods.streamlit.app) *(disponible después del deployment)*

---

## 📋 Descripción

**Smart Scoring** es un sistema automatizado de Machine Learning que predice la **probabilidad de matrícula** (0-100%) de cada lead del CRM, permitiendo al Call Center priorizar contactos y maximizar conversiones.

### 🎯 Problema que Resuelve

- ❌ **Antes**: Asesores llamaban leads por orden de llegada, perdiendo tiempo en contactos de baja calidad
- ✅ **Ahora**: El modelo predice qué leads tienen alta probabilidad de matricularse para llamarlos primero

### 💡 Impacto en el Negocio

- 📈 **Aumento de conversión**: Priorizar leads >60% de probabilidad
- ⚡ **Eficiencia operativa**: Reducir tiempo perdido en llamadas inútiles
- 🎯 **Optimización de marketing**: Identificar qué campañas traen mejores leads
- 🛡️ **Calidad de datos**: Limpieza automática antes de Power BI

### 🏫 Universidades Soportadas

El sistema es **multi-universidad** y funciona con datos de:

| Universidad | Leads Procesables | Estado |
|-------------|-------------------|--------|
| UNAB | 6,238 | ✅ |
| Crexe | 43,953 | ✅ |
| UEES | 27,333 | ✅ |
| Anahuac | 14,992 | ✅ |
| Unisangil | 4,309 | ✅ |
| **TOTAL** | **~97,000** | ✅ |

---

## 🚀 Demo en Vivo

### Opción 1: App Pública (Streamlit Cloud)

Visitá la app en tu navegador:
```
https://smart-scoring-nods.streamlit.app
```

**Características**:
- ✅ Subir archivo CSV o Excel del CRM
- ✅ Procesamiento automático (limpieza + features)
- ✅ Predicción de scores en tiempo real
- ✅ Visualizaciones interactivas
- ✅ Descarga de resultados con scores

### Opción 2: Instalación Local

```bash
# Clonar repositorio
git clone https://github.com/Franco-Arce/Smart-Scoring-Grupo-Nods.git
cd Smart-Scoring-Grupo-Nods

# Instalar dependencias
pip install -r requirements.txt

# Ejecutar app
streamlit run app.py
```

---

## 🚀 Resultados del Modelo

| Métrica | Valor | Significado |
|---------|-------|-------------|
| **AUC-ROC** | 0.927 | Excelente capacidad de separar buenos de malos leads |
| **Accuracy** | 90.91% | Acierta el 91% de las predicciones |
| **Recall** | 83% | Detecta 83% de los leads que SÍ se matriculan |
| **Precision** | 33% | De los que predice como "se matriculará", acierta 33% |

> **Importante**: El Recall alto (83%) es el objetivo principal. Significa que **casi no dejamos pasar leads buenos**, aunque algunos falsos positivos son aceptables.

---

## 📊 Features Más Importantes

El modelo identifica estas variables como las más predictivas:

1. **UTM Source** (34.6%) - Plataforma de origen (Google, Facebook)
2. **UTM Medium** (23.1%) - Tipo de campaña (Paid Social, Organic)
3. **Ratio Llamadas/Días** (10.1%) - Intensidad del seguimiento
4. **Contador Llamadas** (9.1%) - Número total de intentos
5. **Días Gestión** (7.6%) - Tiempo desde primer contacto

---

## 📁 Estructura del Proyecto

```
Prob Leads - Data Science Nods/
│
├── data/
│   ├── Consulta_Base_Unificada_UNAB.xls     # Datos originales del CRM
│   ├── datos_limpios.csv                    # Después de limpieza
│   └── datos_con_features.csv               # Con features creadas
│
├── models/
│   ├── modelo_scoring.pkl                   # Modelo Random Forest entrenado
│   ├── label_encoders.pkl                   # Encoders para categorías
│   ├── metricas_modelo.json                 # Métricas de performance
│   ├── roc_curve.png                        # Curva ROC
│   ├── feature_importance.png               # Importancia de features
│   └── score_distribution.png               # Distribución de scores
│
├── scripts/
│   ├── clean_data.py                        # Paso 1: Limpieza
│   ├── create_features.py                   # Paso 2: Feature Engineering
│   └── train_model.py                       # Paso 3: Entrenamiento
│
├── app.py                                    # Aplicación Streamlit
├── requirements.txt                          # Dependencias Python
└── README.md                                 # Este archivo
```

---

## ⚙️ Instalación y Uso

### 1️⃣ Requisitos Previos

- Python 3.10 o superior
- pip instalado

### 2️⃣ Instalar Dependencias

```bash
pip install -r requirements.txt
```

### 3️⃣ Ejecutar el Pipeline Completo (Opcional)

Si quieres procesar datos nuevos desde cero:

```bash
# Paso 1: Limpiar datos
python scripts/clean_data.py

# Paso 2: Crear features
python scripts/create_features.py

# Paso 3: Entrenar modelo (opcional, ya está entrenado)
python scripts/train_model.py
```

### 4️⃣ Lanzar la Aplicación Web

```bash
streamlit run app.py
```

La app se abrirá en tu navegador en `http://localhost:8501`

---

## 💻 Cómo Usar la App

### Opción 1: Subir Archivo Nuevo

1. Procesa tu archivo Excel del CRM con `clean_data.py` y `create_features.py`
2. En la app, selecciona **"📤 Subir Datos"**
3. Sube el CSV generado (`datos_con_features.csv`)
4. Click en **"🚀 GENERAR SCORES"**
5. Descarga el CSV con la columna `Probabilidad_Matricula` (0-100%)

### Opción 2: Demo con Datos Existentes

1. Selecciona **"📊 Demo con Datos Existentes"**
2. La app cargará automáticamente los datos de entrenamiento
3. Explora los dashboards y top leads

---

## 🧠 Explicación del Proceso

### Paso 1: Limpieza de Datos (`clean_data.py`)

**¿Qué hace?**
- Elimina columnas 100% vacías (Etapa, Canal)
- **Detecta duplicados**: mismo email + mismo programa (409 eliminados)
- Valida emails con expresiones regulares
- Normaliza texto (mayúsculas, espacios)
- Procesa fechas y calcula días de gestión

**Input**: `Consulta_Base_Unificada_UNAB.xls` (6,238 leads)  
**Output**: `datos_limpios.csv` (5,829 leads)

---

### Paso 2: Feature Engineering (`create_features.py`)

**¿Qué hace?**
- Crea 11 features nuevas:
  - `tiene_email`: Flag 1/0 si email válido
  - `whatsapp_entrante_flag`: 1 si escribió por WhatsApp
  - `lead_reciente`: 1 si <7 días
  - `lead_antiguo`: 1 si >30 días
  - `ratio_llamadas_dias`: Llamadas ÷ días
  - `alta_actividad_llamadas`: 1 si >5 llamadas
  - `programa_categoria`: Tecnología, Negocios, Derecho, etc.
  - `base_categoria`: Pregrado, Posgrado, LETO
  - `utm_source_clean`: Google, Facebook, Otros
  - `utm_medium_clean`: Paid Social, Organic, Otros

**Input**: `datos_limpios.csv`  
**Output**: `datos_con_features.csv` (19 columnas)

---

### Paso 3: Entrenamiento del Modelo (`train_model.py`)

**¿Qué hace?**
- Separa datos 80% entrenamiento / 20% prueba
- Entrena **Random Forest** con 100 árboles
- Balancea clases desbalanceadas (solo 5% matriculan)
- Genera métricas y visualizaciones
- Guarda modelo en `modelo_scoring.pkl`

**Parámetros del modelo**:
```python
RandomForestClassifier(
    n_estimators=100,
    max_depth=10,
    min_samples_split=20,
    min_samples_leaf=10,
    class_weight='balanced'
)
```

**Output**: 
- `modelo_scoring.pkl`
- `roc_curve.png`
- `feature_importance.png`
- `metricas_modelo.json`

---

## 📈 Cómo Interpretar los Scores

| Score | Acción Recomendada | Prioridad |
|-------|-------------------|-----------|
| **80-100%** | 🔥 Llamar inmediatamente | Alta |
| **60-79%** | ⚡ Llamar hoy | Media-Alta |
| **30-59%** | 📞 Llamar esta semana | Media |
| **0-29%** | 📧 Enviar email automático | Baja |

---

## 🔗 Integración con n8n y Power BI

### Opción A: n8n (Automático)

1. **n8n Trigger**: Cron diario (ej. 8:00 AM)
2. **HTTP Request**: Llama a API Python en Azure Function
3. **Python Script**: Ejecuta pipeline + predicciones
4. **Update Neotel CRM**: Actualiza campo `score_matricula`
5. **Notificación**: Slack/Email con top 20 leads

### Opción B: Power BI (Manual)

1. Ejecutar pipeline local o en Azure
2. Exportar CSV con scores
3. Importar a Power BI
4. Crear dashboard con:
   - Distribución de scores
   - Top leads por asesor
   - Conversión por canal

---

## 🐛 Troubleshooting

### Error: "Missing optional dependency 'xlrd'"
```bash
pip install xlrd openpyxl
```

### Error: "KeyError: 'Resolución'"
- Asegúrate de que el archivo Excel tenga las columnas originales del CRM

### App no carga modelo
- Verifica que existan los archivos en `models/modelo_scoring.pkl` y `models/label_encoders.pkl`
- Ejecuta `python scripts/train_model.py` para regenerar

---

## 📞 Contacto y Soporte

**Desarrollado por**: Francisco (Data Science)  
**Para**: Grupo Nods / UNAB  
**Fecha**: Diciembre 2025

---

## 📝 Notas Técnicas

### ¿Por qué Random Forest?

- ✅ Maneja bien datos tabulares y categóricos
- ✅ Robusto ante outliers
- ✅ No requiere normalización
- ✅ Interpretable (feature importance)
- ✅ Buen rendimiento sin tunning excesivo

### ¿Por qué Precision es "baja" (33%)?

Es un trade-off intencional:
- **Recall alto (83%)**: No queremos perder leads buenos
- **Precision moderada (33%)**: Aceptamos algunos falsos positivos

**Ejemplo**: Si el modelo dice "Este lead se matriculará", tenemos 33% de certeza. PERO si un lead SÍ se matricula, el modelo lo detectó el 83% de las veces.

Para el Call Center, **es mejor llamar 3 leads (2 falsos positivos + 1 real) que perder 1 lead real**.

---

## 🚀 Próximos Pasos (Roadmap)

- [ ] Deployment en Azure App Service / Functions
- [ ] API REST para integración n8n
- [ ] Dashboard Power BI integrado
- [ ] Reentrenamiento automático mensual
- [ ] A/B Testing con Call Center
- [ ] Alertas push para leads >90%

---

## 📄 Licencia

Proyecto privado de Grupo Nods. Todos los derechos reservados.
