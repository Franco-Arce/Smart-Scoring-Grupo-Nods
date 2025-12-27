# 🚀 Deployment en Streamlit Cloud

Esta guía explica cómo desplegar **Smart Scoring** en Streamlit Cloud para acceso público.

---

## 📋 Pre-requisitos

1. ✅ Repositorio en GitHub: https://github.com/Franco-Arce/Smart-Scoring-Grupo-Nods
2. ✅ Cuenta en Streamlit Cloud (gratis): https://streamlit.io/cloud
3. ✅ Archivos del modelo en `models/` (deben estar en GitHub)

---

## 🔧 Pasos para Deploy

### 1. Verificar que el modelo esté en GitHub

```bash
# Verificar tamaño del modelo
ls -lh models/modelo_scoring.pkl
```

**Importante**: GitHub tiene límite de 100MB por archivo.

- ✅ Si `modelo_scoring.pkl` < 100MB → Subir directamente
- ❌ Si `modelo_scoring.pkl` > 100MB → Usar Git LFS o comprimir

### 2. Subir el Proyecto a GitHub

```bash
# Inicializar git (si no está inicializado)
git init

# Agregar remote
git remote add origin https://github.com/Franco-Arce/Smart-Scoring-Grupo-Nods.git

# Agregar archivos (el .gitignore ya excluye datos sensibles)
git add .

# Commit
git commit -m "Initial commit - Smart Scoring Multi-Universidad"

# Push
git push -u origin main
```

### 3. Conectar con Streamlit Cloud

1. **Ir a**: https://share.streamlit.io/
2. **Sign in** con tu cuenta de GitHub
3. **Click en "New app"**
4. **Configurar**:
   - Repository: `Franco-Arce/Smart-Scoring-Grupo-Nods`
   - Branch: `main`
   - Main file path: `app.py`
   - App URL (custom): `smart-scoring-nods` (o el que prefieras)

5. **Click "Deploy"**
6. **Esperar** ~2-3 minutos

### 4. URL Pública

Tu app estará disponible en:
```
https://smart-scoring-nods.streamlit.app
```

O la URL que elijas en Streamlit Cloud.

---

## ⚙️ Configuración Avanzada (Opcional)

### Secrets Management

Si necesitás variables de entorno o credenciales:

1. En Streamlit Cloud → App settings → Secrets
2. Agregar en formato TOML:

```toml
# .streamlit/secrets.toml (NO subir a GitHub)
[database]
user = "admin"
password = "tu_password"
```

3. Acceder en código:
```python
import streamlit as st
user = st.secrets["database"]["user"]
```

---

## 🐛 Troubleshooting

### Error: "ModuleNotFoundError"
**Solución**: Verificar que `requirements.txt` tenga todas las dependencias.

### Error: "File not found: modelo_scoring.pkl"
**Solución**: Asegurar que la carpeta `models/` y el archivo `.pkl` estén en GitHub.

### App muy lenta
**Solución**: 
- Streamlit Cloud tiene recursos limitados (1GB RAM)
- Considerar reducir tamaño de modelo
- Usar `@st.cache_resource` para cargar modelo (ya implementado)

### Datos de ejemplo no disponibles
**Solución**: La carpeta `data/` está vacía en GitHub por seguridad. La app funcionará solo con archivos que el usuario suba.

---

## 🔒 Seguridad en Producción

### ⚠️ Importante

La app en Streamlit Cloud será **pública**. Cualquiera con el link podrá acceder.

**Riesgos**:
- ❌ No subir datos del CRM a GitHub
- ❌ No hardcodear credenciales en el código
- ✅ Los usuarios pueden subir sus propios CSVs (riesgo bajo)

**Mitigaciones Recomendadas**:

1. **Autenticación** (opcional):
   ```python
   # Agregar contraseña simple
   password = st.text_input("Password", type="password")
   if password != st.secrets["app_password"]:
       st.error("Password incorrecta")
       st.stop()
   ```

2. **Limitar acceso por IP** (requiere plan pago de Streamlit)

3. **Deployment privado**:
   - Usar Streamlit Cloud para equipo privado
   - O deployment en Azure/AWS con autenticación

---

## 📊 Monitoreo

Streamlit Cloud ofrece:
- 📈 Analytics básicos (vistas, users)
- 🔍 Logs de la app
- ⚡ Uso de recursos (CPU, RAM)

Acceder desde: App settings → Analytics

---

## 🔄 Actualizaciones

Cada vez que hagas `git push` a `main`, Streamlit Cloud **redeploya automáticamente**.

```bash
# Hacer cambios
git add .
git commit -m "Mejoras en la app"
git push

# Streamlit Cloud detecta el cambio y redeploya en ~2 min
```

---

## 🌐 URLs de Referencia

- **App en producción**: https://smart-scoring-nods.streamlit.app (después del deploy)
- **Streamlit Cloud Dashboard**: https://share.streamlit.io/
- **GitHub Repo**: https://github.com/Franco-Arce/Smart-Scoring-Grupo-Nods
- **Documentación Streamlit**: https://docs.streamlit.io/streamlit-community-cloud

---

## ✅ Checklist Pre-Deploy

Antes de hacer deploy, verificar:

- [ ] `.gitignore` excluye archivos de datos (`data/*.xls`, `data/*.csv`)
- [ ] `requirements.txt` tiene todas las dependencias
- [ ] `models/modelo_scoring.pkl` existe y < 100MB
- [ ] `models/label_encoders.pkl` existe
- [ ] `app.py` no tiene rutas absolutas (usar `Path(__file__).parent`)
- [ ] README.md tiene instrucciones claras
- [ ] Probar app localmente: `streamlit run app.py`

---

**¿Listo para deploy?** Seguí los pasos arriba y en 5 minutos tendrás la app pública! 🚀
