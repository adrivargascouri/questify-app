#!/usr/bin/env python3
"""
Script de despliegue para inicializar Questify en producción
Ejecutar después del primer despliegue en Render
"""

import os
import sys

# Agregar el directorio raíz al path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from config import ProductionConfig

def deploy():
    """Inicializar la aplicación para producción"""
    print("🚀 Iniciando despliegue de Questify...")

    # Crear app con configuración de producción
    app = create_app(ProductionConfig)

    with app.app_context():
        from modelos.models import db, LootItem
        from flask_migrate import Migrate

        # Inicializar base de datos
        print("📊 Inicializando base de datos...")
        db.create_all()

        # Ejecutar migraciones si existen
        try:
            from flask_migrate import upgrade
            upgrade()
            print("✅ Migraciones aplicadas")
        except Exception as e:
            print(f"⚠️  No se pudieron aplicar migraciones: {e}")

        # Seed de datos iniciales
        print("🎁 Poblando base de datos con items...")
        if not LootItem.query.first():
            # Importar y ejecutar el seed
            exec(open('scripts/seed_db.py').read())
            print("✅ Base de datos poblada")
        else:
            print("ℹ️  Base de datos ya poblada")

    print("🎉 ¡Despliegue completado!")
    print("🌐 Tu app Questify está lista en producción")

if __name__ == '__main__':
    deploy()