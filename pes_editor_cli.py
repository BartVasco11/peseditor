import sys
import os
import shutil
import datetime
from pes_player_data_editor import load_player_data_from_csv, read_player_data, write_player_data

DT04_EXTRACTED_FILES_PATH = "." # Assuming unnamed_0075.bin is in the current directory for simplicity
CSV_FILE_PATH = "." # Assuming Base_de_Dados_CSV_destruncado.csv is in the current directory
UNNAMED_0075_BIN = os.path.join(DT04_EXTRACTED_FILES_PATH, "dt04_extracted_files", "unnamed_0075.bin")
CSV_DATA_FILE = os.path.join(CSV_FILE_PATH, "upload", "Base_de_Dados_CSV_destruncado.csv")
BACKUP_DIR = os.path.join(DT04_EXTRACTED_FILES_PATH, "backups")

def create_backup(file_path):
    if not os.path.exists(file_path):
        print("Erro: Arquivo original {} não encontrado para backup.".format(file_path))
        return None

    if not os.path.exists(BACKUP_DIR):
        os.makedirs(BACKUP_DIR)

    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    file_name = os.path.basename(file_path)
    backup_file_name = "{}_{}{}".format(os.path.splitext(file_name)[0], timestamp, os.path.splitext(file_name)[1])
    backup_path = os.path.join(BACKUP_DIR, backup_file_name)

    try:
        shutil.copy(file_path, backup_path)
        print("Backup de {} criado em {}".format(file_path, backup_path))
        return backup_path
    except Exception as e:
        print("Erro ao criar backup de {}: {}".format(file_path, e))
        return None

def display_player_info(player_info):
    if player_info:
        print("\n--- Detalhes do Jogador ---")
        print("ID: {}".format(player_info["id"]))
        print("Nome: {}".format(player_info["name"]))
        print("Offset do Bloco: 0x{:X}".format(player_info["block_offset"]))
        print("Offset do ID no Bloco: 0x{:X}".format(player_info["id_in_block_offset"]))
        print("Tamanho do ID: {} bytes".format(player_info["id_size"]))
        print("Attack: {}".format(player_info["attack"]))
        print("Defense: {}".format(player_info["defense"]))
        print("Stamina: {}".format(player_info["stamina"]))
        print("Top Speed: {}".format(player_info["top_speed"]))
        print("Dribble Accuracy: {}".format(player_info["dribble_accuracy"]))
        print("Dados Brutos do Bloco (primeiros 16 bytes): {}...".format(player_info["raw_block_data"][:32]))
    else:
        print("Jogador não encontrado ou dados inválidos.")

def main():
    print("Iniciando PES Editor CLI...")

    if not os.path.exists(UNNAMED_0075_BIN):
        print("Erro: Arquivo {} não encontrado. Certifique-se de que o dt04.img foi extraído corretamente.".format(UNNAMED_0075_BIN))
        sys.exit(1)
    if not os.path.exists(CSV_DATA_FILE):
        print("Erro: Arquivo {} não encontrado. Certifique-se de que o CSV da base de dados está presente.".format(CSV_DATA_FILE))
        sys.exit(1)

    player_data_csv = load_player_data_from_csv(CSV_DATA_FILE)
    if not player_data_csv:
        print("Erro: Não foi possível carregar os dados dos jogadores do CSV.")
        sys.exit(1)

    # Criar um backup do arquivo binário antes de qualquer modificação
    create_backup(UNNAMED_0075_BIN)

    while True:
        print("\nOpções:")
        print("1. Buscar jogador por ID")
        print("2. Editar atributos de jogador por ID")
        print("3. Sair")
        choice = input("Escolha uma opção: ")

        if choice == "1":
            try:
                player_id = int(input("Digite o ID do jogador: "))
                player_info = read_player_data(UNNAMED_0075_BIN, player_id, player_data_csv)
                display_player_info(player_info)
            except ValueError:
                print("ID inválido. Por favor, digite um número.")
        elif choice == "2":
            try:
                player_id = int(input("Digite o ID do jogador para editar: "))
                player_info = read_player_data(UNNAMED_0075_BIN, player_id, player_data_csv)
                if player_info:
                    display_player_info(player_info)
                    print("\nDigite os novos valores para os atributos (deixe em branco para manter o atual):")
                    new_attributes = {}
                    try:
                        attack_input = input("Attack (atual: {}) [0-255]: ".format(player_info["attack"]))
                        if attack_input: new_attributes["attack"] = int(attack_input)
                        
                        defense_input = input("Defense (atual: {}) [0-255]: ".format(player_info["defense"]))
                        if defense_input: new_attributes["defense"] = int(defense_input)
                        
                        stamina_input = input("Stamina (atual: {}) [0-255]: ".format(player_info["stamina"]))
                        if stamina_input: new_attributes["stamina"] = int(stamina_input)
                        
                        top_speed_input = input("Top Speed (atual: {}) [0-255]: ".format(player_info["top_speed"]))
                        if top_speed_input: new_attributes["top_speed"] = int(top_speed_input)
                        
                        dribble_accuracy_input = input("Dribble Accuracy (atual: {}) [0-255]: ".format(player_info["dribble_accuracy"]))
                        if dribble_accuracy_input: new_attributes["dribble_accuracy"] = int(dribble_accuracy_input)

                        # Validar valores
                        for attr, value in new_attributes.items():
                            if not (0 <= value <= 255):
                                raise ValueError("Valor inválido para {}. Deve estar entre 0 e 255.".format(attr))

                        write_player_data(UNNAMED_0075_BIN, player_info, new_attributes)
                        print("Atributos atualizados com sucesso!")
                        updated_player_info = read_player_data(UNNAMED_0075_BIN, player_id, player_data_csv)
                        display_player_info(updated_player_info)

                    except ValueError as e:
                        print("Erro ao editar atributos: {}. Certifique-se de que os valores são números inteiros entre 0 e 255.".format(e))
                else:
                    print("Jogador não encontrado.")
            except ValueError:
                print("ID inválido. Por favor, digite um número.")
        elif choice == "3":
            print("Saindo do editor.")
            break
        else:
            print("Opção inválida. Por favor, tente novamente.")

if __name__ == "__main__":
    main()


