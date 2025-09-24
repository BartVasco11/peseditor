import os
import shutil
import datetime

# Define the path to the unnamed_0075.bin file
DT04_EXTRACTED_FILES_PATH = "."
UNNAMED_0075_BIN = os.path.join(DT04_EXTRACTED_FILES_PATH, "dt04_extracted_files", "unnamed_0075.bin")
BACKUP_DIR = os.path.join(DT04_EXTRACTED_FILES_PATH, "backups")

def create_backup(file_path):
    if not os.path.exists(file_path):
        print(f"Erro: Arquivo original {file_path} não encontrado para backup.")
        return None

    if not os.path.exists(BACKUP_DIR):
        os.makedirs(BACKUP_DIR)

    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    file_name = os.path.basename(file_path)
    backup_file_name = f"{os.path.splitext(file_name)[0]}_{timestamp}{os.path.splitext(file_name)[1]}"
    backup_path = os.path.join(BACKUP_DIR, backup_file_name)

    try:
        shutil.copy(file_path, backup_path)
        print(f"Backup de {file_path} criado em {backup_path}")
        return backup_path
    except Exception as e:
        print(f"Erro ao criar backup de {file_path}: {e}")
        return None

if __name__ == "__main__":
    print("Iniciando sistema de backup...")
    created_backup = create_backup(UNNAMED_0075_BIN)
    if created_backup:
        print("Backup concluído com sucesso.")
    else:
        print("Falha ao criar backup.")


