# db.py

import psycopg2

# 🔧 Configuración de conexión a PostgreSQL
DB_HOST = "localhost"           # o "192.168.2.38" si te conectas desde otro PC
DB_PORT = "5432"                # Puerto por defecto
DB_NAME = "inventario"          # ⚠️ Este nombre debe coincidir exactamente con tu base
DB_USER = "postgres"
DB_PASSWORD = "50p0rt3"

def conectar():
    return psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD
    )


