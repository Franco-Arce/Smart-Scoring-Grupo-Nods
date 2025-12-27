# 🚀 Cómo Subir a GitHub (Sin Git Instalado)

Git no está instalado en tu sistema. Tenés 2 opciones:

---

## Opción 1: Usar GitHub Desktop (Recomendado - Más Fácil) ✅

### 1. Instalar GitHub Desktop

1. Descargar de: https://desktop.github.com/
2. Instalar y abrir
3. Sign in con tu cuenta de GitHub

### 2. Clonar tu Repositorio

1. En GitHub Desktop → **File** → **Clone repository**
2. Seleccionar: `Franco-Arce/Smart-Scoring-Grupo-Nods`
3. Elegir carpeta local (ej: `C:\GitHub\Smart-Scoring-Grupo-Nods`)
4. Click **Clone**

### 3. Copiar tus Archivos

1. Abrir la carpeta clonada en el Explorador de Windows
2. **Copiar TODOS los archivos** del proyecto actual a la carpeta clonada:
   
   **Desde**:
   ```
   C:\Users\franc\OneDrive\Escritorio\Mis Cosas\Prob Leads - Data Science Nods\
   ```
   
   **Hacia**:
   ```
   C:\GitHub\Smart-Scoring-Grupo-Nods\
   ```
   
   **Importante**: No copiar la carpeta `data/` con archivos `.xls` (datos sensibles)

### 4. Commit y Push

1. Volver a GitHub Desktop
2. Verás todos los archivos en "Changes"
3. Escribir mensaje commit:
   ```
   feat: Smart Scoring system with multi-university support
   
   - ML model with 92.7% AUC-ROC
   - Support for 5 universities
   - Streamlit web app
   ```
4. Click **"Commit to main"**
5. Click **"Push origin"**

✅ ¡Listo! Los archivos están en GitHub.

---

## Opción 2: Upload Directo en GitHub Web ⚡

### Paso 1: Ir al Repositorio

1. Abrir: https://github.com/Franco-Arce/Smart-Scoring-Grupo-Nods

### Paso 2: Subir Archivos

**Método A: Drag & Drop**
1. Click en **"Add file"** → **"Upload files"**
2. Arrastrar carpetas/archivos desde el Explorador
3. **NO subir**: carpeta `data/` con archivos `.xls` o `.csv`
4. Escribir mensaje: "Initial commit - Smart Scoring"
5. Click **"Commit changes"**

**Método B: Archivo por Archivo** (tedioso)
1. Subir cada archivo importante manualmente
2. Mantener la estructura de carpetas

---

## Opción 3: Instalar Git y Usar Comandos

### 1. Instalar Git

**PowerShell (Como Administrador)**:
```powershell
# Opción A: Con winget
winget install Git.Git

# Opción B: Descargar manualmente
# Ir a: https://git-scm.com/download/win
```

### 2. Reiniciar PowerShell

Cerrar y abrir nueva terminal.

### 3. Configurar Git

```powershell
git config --global user.name "Franco Arce"
git config --global user.email "tu-email@gmail.com"
```

### 4. Subir Proyecto

```powershell
cd "C:\Users\franc\OneDrive\Escritorio\Mis Cosas\Prob Leads - Data Science Nods"

git init
git remote add origin https://github.com/Franco-Arce/Smart-Scoring-Grupo-Nods.git
git add .
git commit -m "Initial commit - Smart Scoring multi-universidad"
git push -u origin main
```

---

## ⚠️ Archivos que NO Deben Subirse

El `.gitignore` ya está configurado para excluir:

- ❌ `data/*.xls` - Datos del CRM (SENSIBLE)
- ❌ `data/*.xlsx` - Datos del CRM
- ❌ `data/*.csv` - Datos procesados
- ✅ `data/README.md` - SÍ se sube (es documentación)

### Verificar antes de subir

Si usás Opción 2 (web), asegurate de NO subir:
- `Consulta_Base_Unificada_UNAB.xls`
- `Consulta_Base_Unificada_UEES.xls`
- `Consulta_Base_Unificada_Anahuac.xls`
- `Consulta_Base_Unificada_Unisangil.xls`
- `Reporte_Bases_Unificadas_Crexe.xls`
- Archivos `.csv` en `data/`

---

## ✅ Archivos Importantes que SÍ Subir

```
✓ app.py
✓ requirements.txt
✓ README.md
✓ .gitignore
✓ DEPLOYMENT.md
✓ GUIA_DEPLOYMENT_RAPIDO.md
✓ models/ (toda la carpeta)
✓ scripts/ (toda la carpeta)
✓ data/README.md (solo el README, NO los .xls)
```

---

## 🌐 Después de Subir a GitHub

1. Ir a: https://share.streamlit.io/
2. Sign in con GitHub
3. Click "New app"
4. Seleccionar: `Franco-Arce/Smart-Scoring-Grupo-Nods`
5. Main file: `app.py`
6. Deploy!

Tu app estará en: `https://smart-scoring-nods.streamlit.app`

---

**Recomendación**: Usar **Opción 1 (GitHub Desktop)** - es la más fácil si no tenés Git instalado.
