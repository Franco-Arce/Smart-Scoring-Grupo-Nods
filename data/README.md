# 📁 Data Directory

Este directorio contiene los datos del CRM de las universidades del Grupo Nods.

## ⚠️ Importante - Datos No Incluidos en GitHub

Por razones de **privacidad y seguridad**, los archivos de datos no están incluidos en este repositorio público:

- ❌ `Consulta_Base_Unificada_UNAB.xls`
- ❌ `Consulta_Base_Unificada_UEES.xls`
- ❌ `Consulta_Base_Unificada_Anahuac.xls`
- ❌ `Consulta_Base_Unificada_Unisangil.xls`
- ❌ `Reporte_Bases_Unificadas_Crexe.xls`
- ❌ Archivos procesados (`.csv`)

## 📥 Para Usuarios Internos del Grupo Nods

Si sos parte del equipo y tenés acceso a los datos del CRM:

1. Coloca tus archivos `.xls` o `.xlsx` del CRM en esta carpeta
2. La app detectará automáticamente el formato de tu universidad
3. Procesará los datos y generará scores de matrícula

## 🎯 Formato Esperado

El sistema es compatible con archivos que contengan las siguientes columnas (nombres pueden variar):

### Columnas Esenciales:
- `dcontacto` o `Idcontacto` - ID único del lead
- `Nombre y Apellido` - Nombre del prospecto
- `TELTELEFONO` - Teléfono de contacto
- `EMLMAIL` - Email
- `Programa interes` - Carrera/programa de interés
- `Resolución` - Estado del lead (Matriculado, No contesta, etc.)

### Columnas Opcionales (mejoran el modelo):
- `CONTADOR_LLAMADOS_TEL` - Número de llamadas realizadas
- `Llamadas_discador` - Llamadas automáticas
- `WhatsApp entrante` - Contacto por WhatsApp
- `Fecha insert Lead` - Fecha de creación del lead
- `UTM Medium`, `UTM Source` - Origen de marketing
- `Base de datos` - Tipo de lead (Pregrado, Posgrado)

## 🔒 Seguridad

Los datos del CRM contienen **información personal identificable (PII)** y están protegidos por:

1. `.gitignore` - Excluye archivos de datos del repositorio
2. Procesamiento local - Los datos nunca salen de tu máquina
3. Sin conexión a internet durante procesamiento

## 📊 Datos de Demo

Para probar la app sin datos reales, podés crear un archivo CSV de ejemplo con datos ficticios siguiendo la estructura arriba.
