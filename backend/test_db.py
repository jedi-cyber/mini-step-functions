from app.database.connection import engine

try:
    with engine.connect() as connection:
        print("Conexión a PostgreSQL exitosa")
except Exception as e:
    print("Error de conexión:")
    print(e)