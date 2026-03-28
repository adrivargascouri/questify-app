# Questify - Gamified Task Manager

Una aplicación web que convierte tus tareas diarias en una aventura de videojuego con sistema de recompensas.

## 🚀 Despliegue Rápido en Render

### 1. Preparar el código

```bash
# Crear requirements.txt (ya hecho)
pip freeze > requirements.txt

# Los archivos necesarios ya están creados:
# - requirements.txt
# - runtime.txt
# - Procfile
```

### 2. Subir a GitHub

1. Crear un repositorio en GitHub
2. Subir todo el código del proyecto

### 3. Desplegar en Render

1. Ir a [render.com](https://render.com) y crear cuenta
2. Click "New +" → "Web Service"
3. Conectar tu repositorio de GitHub
4. Configurar:
   - **Name**: questify-app
   - **Environment**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python app.py`

### 4. Configurar Base de Datos

Después del primer despliegue, ejecutar en Render Shell:

```bash
python deploy.py
```

O manualmente:

```bash
flask db init
flask db migrate
flask db upgrade
python scripts/seed_db.py
```

## 🎮 Características

- ✅ Sistema de usuarios con registro/login
- ✅ Gestión de tareas con categorías y dificultad
- ✅ Sistema de recompensas con 20 items coleccionables
- ✅ Niveles y puntos de experiencia
- ✅ Interfaz moderna con animaciones
- ✅ API REST completa

## 🛠️ Desarrollo Local

```bash
# Instalar dependencias
pip install -r requirements.txt

# Inicializar base de datos
flask db init
flask db migrate
flask db upgrade
python scripts/seed_db.py

# Ejecutar
python app.py
```

## 📊 Tecnologías

- **Backend**: Flask + SQLAlchemy
- **Frontend**: Vanilla JS + CSS moderno
- **Base de datos**: SQLite (fácil migración a PostgreSQL)
- **Despliegue**: Render (gratuito con límites generosos)

¡Tu app estará online en minutos! 🎉
