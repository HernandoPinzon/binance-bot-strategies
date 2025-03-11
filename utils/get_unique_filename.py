import os


def get_unique_filename(file_path):
    """Genera un nombre de archivo único agregando V2, V3, etc., si el archivo ya existe."""
    base, ext = os.path.splitext(file_path)
    counter = 2
    new_file_path = file_path

    while os.path.exists(new_file_path + ".csv"):
        new_file_path = f"{base}_V{counter}{ext}"
        counter += 1
    print(f"Guardando en {new_file_path}")
    return new_file_path
