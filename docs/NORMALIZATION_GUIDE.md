# Guía de Normalización de Datos Multi-Universidad

## Descripción General

Este sistema normaliza automáticamente los datos de CRM de diferentes universidades del Grupo Nods para garantizar consistencia en el entrenamiento de modelos de Machine Learning.

**Universidades soportadas**: UNAB, Crexe, UEES, Anahuac, Unisangil

---

## Proceso de Normalización

### 1. Normalización de Nombres de Columnas

El sistema aplica automáticamente las siguientes transformaciones:

#### Eliminación de Espacios

Todas las columnas con espacios al final son normalizadas:
- `"Resolución "` → `"Resolución"`
- `"Fecha insert Lead "` → `"Fecha insert Lead"`

#### Mapeo de Nombres

| Nombre Original | Nombre Estándar | Universidades Afectadas |
|----------------|-----------------|-------------------------|
| `Resolucion` | `Resolución` | Crexe, UEES, Anahuac |
| `Idcontacto` | `dcontacto` | Crexe, UEES, Anahuac |
| `Lamadas_discador` | `Llamadas_discador` | Crexe, UEES, Anahuac |
| `CHKENTRANTEWHATSAPP` | `WhatsApp entrante` | Crexe, UEES, Anahuac |
| `TXTESTADOPRINCIPAL` | `Estado principal` | Crexe, UEES, Anahuac |
| `Contador de Llamadas` | `CONTADOR_LLAMADOS_TEL` | UEES |
| `Fecha Inserción Leads` | `Fecha insert Lead` | UEES |
| `UTM Origen` | `UTM Source` | UEES |
| `Ultima resolucion` | `Ultima resolución` | Crexe, UEES, Anahuac |
| `TELWHATSAPP` | `WhatsApp` | Crexe, UEES, Anahuac |

---

### 2. Normalización de Valores de Resolución

Los valores de la columna `Resolución` se categorizan automáticamente:

#### Categoría: Success (Matriculado = 1)

Valores que indican conversión exitosa:
- `Matriculado`
- `Matriculado / Inscripto`
- `Ya matriculado en Anáhuac`
- `Admitido`
- `Inscripto en curso`
- `Ya es alumno de la universidad`

#### Categoría: In Progress (Potencial conversión)

Valores que indican proceso en curso:
- `En proceso de pago`
- `En proceso de pago - No contesta`
- `Oportunidad de venta`
- `Oportunidad de venta - No contesta`
- `Compromiso pago - Cartera`
- `Compromiso pago - cartera`
- `Analizando propuesta`

#### Categoría: Rejected - Enrolled Elsewhere

- `Inscripto en otra universisdad`
- `Inscripto en otra universidad`

#### Categoría: Rejected - No Contact

- `No contesta`
- `NotProcessed`
- `NoAnswerDialer`
- `Buzon de voz`
- `AnswerAnsweringMachineDialer`
- `UnallocatedDialer`
- Y otros valores relacionados con falta de contacto

#### Categoría: Rejected - Phone Issue

- `Telefono erroneo o fuera de servicio`
- `Teléfono erróneo o fuera de servicio`

#### Categoría: Rejected - WhatsApp Issue

- `Deja de responder Whatsapp`
- `Dejo de responder Whatsapp`
- `Responde mensaje de Whastapp`

#### Categoría: Rejected - Not Interested

- `No es la oferta buscada`
- `Le parece caro`
- `Motivos personales`
- `Pide no ser llamado`
- `Spam - Desconoce haber solicitado informacion`
- Y otros valores relacionados con rechazo

---

### 3. Normalización de Valores Dentro de Columnas

Además de normalizar nombres de columnas, el sistema también normaliza los **valores** dentro de ciertas columnas para garantizar consistencia:

#### Canal
Unifica variaciones de escritura:
- `"wsp"`, `"WSP"`, `"Wsp"`, `"whatsapp"`, `"Whatsapp"` → `"whatsapp"`
- `"wa"`, `"whats"` → `"whatsapp"`
- Todo convertido a minúsculas
- Valores vacíos → `"no_especificado"`

**Ejemplo:**
```
Antes:  ["wsp", "WSP", "Wsp", "whatsapp"]
Después: ["whatsapp", "whatsapp", "whatsapp", "whatsapp"]
```

#### Programa interes
- Todo convertido a MAYÚSCULAS
- Espacios eliminados al inicio/final
- Valores vacíos → `"NO ESPECIFICADO"`

**Ejemplo:**
```
Antes:  ["Tecnología en Farmacia", "tecnología en farmacia  "]
Después: ["TECNOLOGÍA EN FARMACIA", "TECNOLOGÍA EN FARMACIA"]
```

#### UTM Source, UTM Medium, UTM Campaing, UTM Content
- Todo convertido a minúsculas
- Espacios eliminados
- Valores vacíos o `"nan"` → `"no_disponible"`

**Ejemplo:**
```
Antes:  ["Google", "GOOGLE", "nan", null]
Después: ["google", "google", "no_disponible", "no_disponible"]
```

#### Base de datos
- Espacios eliminados al inicio/final
- Formato consistente preservado

---

## Uso del Sistema

### Procesar Datos de Todas las Universidades

```bash
python scripts/prepare_multi_university_data.py
```

**Salida:**
- `data/datos_multi_universidad_limpios.csv` - Datos normalizados y limpios
- `data/datos_multi_universidad_features.csv` - Datos con features de ML

### Validar Normalización

```bash
# Validación básica
python scripts/validate_normalization.py

# Validación completa con resoluciones y calidad
python scripts/validate_normalization.py --check-resolutions --check-quality
```

### Actualizar Configuración

Si se agregan nuevas universidades o se detectan nuevas variaciones:

```bash
python scripts/create_normalization_config.py
```

Esto regenerará `config/normalization_config.json` con los nuevos mapeos detectados.

---

## Configuración

### Archivo: `config/normalization_config.json`

Este archivo centraliza todas las reglas de normalización:

```json
{
  "column_mappings": {
    "Resolucion": "Resolución",
    "Idcontacto": "dcontacto",
    ...
  },
  "resolution_mappings": {
    "success": ["Matriculado", "Admitido", ...],
    "in_progress": ["En proceso de pago", ...],
    ...
  },
  "resolution_to_binary": {
    "success": 1,
    "in_progress": 0,
    ...
  }
}
```

---

## Columnas Resultantes

Después de la normalización, todas las universidades tendrán las siguientes **32 columnas**:

### Columnas de Identificación
- `dcontacto` - ID único del contacto
- `universidad` - Universidad de origen

### Columnas de Contacto
- `EMLMAIL` - Email
- `TELTELEFONO` - Teléfono
- `WhatsApp` - WhatsApp
- `Nombre y Apellido` - Nombre completo

### Columnas de Resolución
- `Resolución` - Valor original de resolución
- `resolucion_categoria` - Categoría normalizada
- `resolucion_binaria` - 1 = success, 0 = otros
- `target` - Variable objetivo para ML (igual a resolucion_binaria)
- `Ultima resolución` - Última resolución registrada

### Columnas de Actividad
- `CONTADOR_LLAMADOS_TEL` - Número de llamadas telefónicas
- `Llamadas_discador` - Llamadas del discador
- `WhatsApp entrante` - Indicador de WhatsApp entrante

### Columnas Temporales
- `Fecha insert Lead` - Fecha de creación del lead
- `Fecha y hora de actualización` - Última actualización
- `Fecha y hora del próximo llamado` - Próximo contacto programado
- `dias_gestion` - Días desde creación hasta última actualización

### Columnas de Programa
- `Programa interes` - Programa de interés
- `Base de datos` - Base de datos de origen
- `Canal` - Canal de adquisición

### Columnas UTM
- `UTM Source` - Fuente de tráfico
- `UTM Medium` - Medio de tráfico
- `UTM Campaing` - Campaña
- `UTM Content` - Contenido
- `UTM TERM` - Término

### Columnas de Estado
- `Estado principal` - Estado principal del lead
- `Etapa` - Etapa en el funnel

### Columnas de Operador
- `Operador` - ID del operador
- `Nombre Operador` - Nombre del operador
- `Mensaje` - Mensajes/notas

### Columnas Derivadas
- `email_valido` - Indicador de email válido

---

## Agregar Nueva Universidad

### Paso 1: Colocar Archivo

Coloca el archivo `.xls` en la carpeta `data/`:
```
data/Consulta_Base_Unificada_NuevaUniversidad.xls
```

### Paso 2: Analizar Diferencias

```bash
python scripts/analizar_diferencias_universidades.py
```

Revisa el output para identificar:
- Nombres de columnas diferentes
- Valores de Resolución únicos
- Formatos especiales

### Paso 3: Actualizar Configuración

Edita `config/normalization_config.json` y agrega:

1. **Mapeos de columnas** (si hay nombres diferentes):
```json
"column_mappings": {
  "NombreEspecifico": "NombreEstandar",
  ...
}
```

2. **Valores de resolución** (si hay nuevos valores):
```json
"resolution_mappings": {
  "success": ["Nuevo valor de éxito", ...],
  ...
}
```

3. **Nombre de universidad**:
```json
"universities": ["UNAB", "Crexe", "UEES", "Anahuac", "Unisangil", "NuevaUniversidad"]
```

### Paso 4: Actualizar Script

Edita `scripts/prepare_multi_university_data.py` y agrega la universidad:

```python
archivos_universidades = {
    'UNAB': DATA_DIR / 'Consulta_Base_Unificada_UNAB.xls',
    ...
    'NuevaUniversidad': DATA_DIR / 'Consulta_Base_Unificada_NuevaUniversidad.xls'
}
```

### Paso 5: Probar

```bash
python scripts/prepare_multi_university_data.py
python scripts/validate_normalization.py --check-resolutions
```

---

## Solución de Problemas

### Error: "Columna requerida faltante"

**Causa**: La universidad no tiene una columna crítica.

**Solución**: 
1. Verifica si la columna tiene otro nombre
2. Agrega el mapeo en `column_mappings`
3. Si la columna no existe, considera si es realmente requerida

### Advertencia: "Resoluciones no categorizadas"

**Causa**: Hay valores de Resolución que no están en la configuración.

**Solución**:
1. Revisa los valores mostrados
2. Decide a qué categoría pertenecen
3. Agrégalos a `resolution_mappings` en la categoría apropiada

### Error: "Tipos de datos incorrectos"

**Causa**: Los tipos de datos no coinciden con lo esperado.

**Solución**:
- Esto es generalmente una advertencia, no un error crítico
- Verifica que las conversiones de tipos se hagan correctamente en el script

---

## Métricas de Calidad

Después de la normalización, el sistema reporta:

### Por Universidad
- **Total de leads** procesados
- **Tasa de conversión** (target = 1)
- **Mapeos aplicados** (transformaciones de columnas)
- **Resoluciones no categorizadas**

### Global
- **Total de leads**: 133,209 (después de eliminar duplicados)
- **Universidades**: 5
- **Features**: 42
- **Target positivos**: 1,711 (1.28%)

### Distribución por Universidad
- **UNAB**: 57,707 leads (1.95% conversión)
- **Crexe**: 31,807 leads (0.27% conversión)
- **UEES**: 25,767 leads (0.86% conversión)
- **Anahuac**: 13,663 leads (1.67% conversión)
- **Unisangil**: 4,265 leads (0.33% conversión)

---

## Columnas de Data Leakage

⚠️ **IMPORTANTE**: Las siguientes columnas contienen información del futuro y **NO deben usarse como features** para el modelo:

- `Resolución` - Es el target
- `Resolucion` - Variante del target
- `Ultima resolución` - Información posterior
- `Ultima resolucion` - Variante
- `Estado principal` - Puede contener resultado final
- `TXTESTADOPRINCIPAL` - Variante
- `Etapa` - Puede indicar resultado

Estas columnas se mantienen en el dataset para análisis, pero el script de entrenamiento debe excluirlas.

---

## Contacto y Soporte

Para preguntas o problemas con la normalización:
1. Revisa esta guía
2. Ejecuta el script de validación
3. Consulta los logs de procesamiento
4. Revisa `config/normalization_config.json`
