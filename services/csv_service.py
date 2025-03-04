import csv
import os

def save_to_csv(file_path, headers, row_data, delimiter=";"):
    """Guarda una fila en un archivo CSV, creando el archivo si no existe."""
    file_exists = os.path.isfile(file_path)

    with open(file_path, mode="a", newline="") as file:
        writer = csv.writer(file, delimiter=delimiter)

        # Escribir encabezado si el archivo es nuevo
        if not file_exists:
            writer.writerow(headers)

        # Escribir los datos en el archivo
        writer.writerow(row_data)
