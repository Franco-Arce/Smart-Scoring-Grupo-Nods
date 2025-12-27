# 🚀 Guía Rápida de Deployment

## ✅ Pre-requisitos Completados

- [x] `.gitignore` creado (excluye datos sensibles)
- [x] `requirements.txt` listo
- [x] Modelo < 100MB (0.68 MB ✅)
- [x] README actualizado
- [x] Repositorio GitHub creado: https://github.com/Franco-Arce/Smart-Scoring-Grupo-Nods

---

## 📦 Paso 1: Subir a GitHub

Ejecutá estos comandos en la terminal (PowerShell):

```powershell
# Navegar al proyecto
cd "c:\Users\franc\OneDrive\Escritorio\Mis Cosas\Prob Leads - Data Science Nods"

# Inicializar git (si no está)
git init

# Configurar usuario (si no está configurado)
git config user.name "Franco-Arce"
git config user.email "tu-email@gmail.com"  # Cambiá por tu email

# Agregar remote
git remote add origin https://github.com/Franco-Arce/Smart-Scoring-Grupo-Nods.git

# Verificar qué archivos se van a subir (debe excluir data/*.xls)
git status

# Agregar todos los archivos
git add .

# Commit
git commit -m "feat: Smart Scoring system with multi-university support

- ML model with 92.7% AUC-ROC
- Support for 5 universities (UNAB, Crexe, UEES, Anahuac, Unisangil)
- Streamlit web app with automatic data processing
- Multi-format CSV/Excel compatibility"

# Push (te va a pedir autenticación)
git push -u origin main
```

### ⚠️ Si git push falla

Puede que necesites autenticarte. Opciones:

**Opción A: GitHub Personal Access Token**
1. Ir a: https://github.com/settings/tokens
2. "Generate new token" → "Classic"
3. Seleccionar scope: `repo`
4. Copiar el token
5. Al hacer `git push`, usar el token como password

**Opción B: GitHub CLI**
```powershell
# Instalar GitHub CLI
winget install GitHub.cli

# Autenticar
gh auth login

# Luego hacer push normalmente
git push -u origin main
```

---

## 🌐 Paso 2: Deploy en Streamlit Cloud

### 1. Crear Cuenta en Streamlit Cloud

1. Ir a: https://share.streamlit.io/
2. Click en **"Continue with GitHub"**
3. Autorizar Streamlit a acceder a tus repos

### 2. Crear Nueva App

1. Click en **"New app"**
2. Completar:
   ```
   Repository: Franco-Arce/Smart-Scoring-Grupo-Nods
   Branch: main
   Main file path: app.py
   ```
3. **App URL** (opcional): `smart-scoring-nods`
4. Click en **"Deploy!"**

### 3. Esperar Deployment

- ⏳ Primeras veces: ~3-5 minutos
- ✅ Deployments futuros: ~1-2 minutos

---

## 🎯 Paso 3: Verificar App

Una vez deployado, la app estará en:
```
https://smart-scoring-nods.streamlit.app
```

O la URL que elegiste.

### Probar que funciona:

1. ✅ La app carga sin errores
2. ✅ El sidebar muestra métricas del modelo
3. ✅ Modo "Demo" funciona (si hay `data/datos_con_features.csv`)
4. ✅ Modo "Subir Datos" permite upload de CSV

---

## 🔧 Troubleshooting Común

### Error: "No module named 'openpyxl'"
**Solución**: Verificar `requirements.txt` tiene `openpyxl==3.1.5`

### Error: "ModuleNotFoundError: No module named 'streamlit'"
**Solución**: El `requirements.txt` debe estar en el root del proyecto

### App carga pero no muestra el modelo
**Solución**: Verificar que `models/modelo_scoring.pkl` esté en GitHub:
```bash
git ls-files models/
```

### Los datos de demo no están
**Esperado**: La carpeta `data/` está vacía en GitHub (por seguridad). Los usuarios deben subir sus propios archivos.

---

## 🔄 Actualizar la App Deployada

Cada vez que hagas cambios:

```powershell
git add .
git commit -m "Descripción del cambio"
git push

# Streamlit Cloud redeploya automáticamente en ~1-2 min
```

---

## 📊 Links Útiles

- **GitHub Repo**: https://github.com/Franco-Arce/Smart-Scoring-Grupo-Nods
- **Streamlit Cloud**: https://share.streamlit.io/
- **App Pública**: https://smart-scoring-nods.streamlit.app *(después del deploy)*

---

## ✅ Checklist Final

Antes de compartir la app públicamente:

- [ ] Probaste subir un archivo CSV de prueba
- [ ] Las visualizaciones se ven correctamente
- [ ] Los scores se generan sin errores
- [ ] La descarga de CSV funciona
- [ ] README en GitHub está actualizado con instrucciones

---

**¿Listo?** Ejecutá los comandos de "Paso 1" para subir a GitHub! 🚀
