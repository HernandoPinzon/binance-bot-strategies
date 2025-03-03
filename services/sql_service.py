import sqlite3


def save_to_sql(db_path, table_name, columns, row_data):
    """Guarda una fila en la base de datos SQLite, creando la tabla si no existe."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Crear la tabla si no existe
    column_definitions = ", ".join([f"{col} TEXT" for col in columns])
    cursor.execute(f"CREATE TABLE IF NOT EXISTS {table_name} ({column_definitions})")

    # Insertar los datos
    placeholders = ", ".join(["?" for _ in columns])
    cursor.execute(f"INSERT INTO {table_name} VALUES ({placeholders})", row_data)

    conn.commit()
    conn.close()

    print(f"💾 Datos guardados en la tabla {table_name} de {db_path}")
