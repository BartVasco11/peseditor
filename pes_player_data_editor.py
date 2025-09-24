import struct
import csv

def load_player_data_from_csv(csv_file_path):
    player_data = {}
    with open(csv_file_path, mode='r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            try:
                player_id = int(row["id"])
                player_data[player_id] = row
            except ValueError:
                continue # Skip rows with invalid Player ID
    return player_data

def find_player_block_and_offset(file_path, player_id, block_size=64):
    with open(file_path, 'rb') as f:
        content = f.read()

    num_blocks = len(content) // block_size

    # Prioritized offsets for 2-byte player IDs based on previous analysis
    id_offsets_2byte = [0x6, 0xE, 0x2, 0xA, 0x7, 0x3, 0xB, 0xF, 0x4, 0x0, 0xC, 0xD, 0x9, 0x8, 0x5, 0x1]
    id_offsets_4byte = [0xE, 0x2, 0x6, 0xA, 0x7, 0x3, 0xF, 0xB, 0x4, 0xC, 0x0, 0x8]

    for i in range(num_blocks):
        block_offset = i * block_size
        block_data = content[block_offset : block_offset + block_size]

        if len(block_data) == block_size:
            # Try 2-byte IDs first
            for offset in id_offsets_2byte:
                if offset + 2 <= block_size:
                    try:
                        current_id = struct.unpack('<H', block_data[offset : offset + 2])[0]
                        if current_id == player_id:
                            return block_offset, offset, 2 # Found 2-byte ID
                    except struct.error:
                        pass
            
            # If not found, try 4-byte IDs
            for offset in id_offsets_4byte:
                if offset + 4 <= block_size:
                    try:
                        current_id = struct.unpack('<I', block_data[offset : offset + 4])[0]
                        if current_id == player_id:
                            return block_offset, offset, 4 # Found 4-byte ID
                    except struct.error:
                        pass
    return None, None, None # Player ID not found

def read_player_data(file_path, player_id, csv_player_data):
    block_offset, id_in_block_offset, id_size = find_player_block_and_offset(file_path, player_id)

    if block_offset is None:
        print(f"Jogador com ID {player_id} não encontrado no arquivo.")
        return None

    with open(file_path, 'rb') as f:
        f.seek(block_offset)
        block_data = f.read(64)

    player_name = csv_player_data.get(player_id, {}).get("Name", "Unknown Player")

    # Placeholder for attribute decoding - these offsets are still speculative
    # Based on previous analysis, 0x10 and 0x11 were potential attribute locations
    attack = struct.unpack('<B', block_data[0x10:0x11])[0] if 0x10 + 1 <= len(block_data) else 0
    defense = struct.unpack('<B', block_data[0x11:0x12])[0] if 0x11 + 1 <= len(block_data) else 0
    stamina = struct.unpack('<B', block_data[0x12:0x13])[0] if 0x12 + 1 <= len(block_data) else 0
    top_speed = struct.unpack('<B', block_data[0x13:0x14])[0] if 0x13 + 1 <= len(block_data) else 0
    dribble_accuracy = struct.unpack('<B', block_data[0x14:0x15])[0] if 0x14 + 1 <= len(block_data) else 0

    return {
        "id": player_id,
        "name": player_name,
        "block_offset": block_offset,
        "id_in_block_offset": id_in_block_offset,
        "id_size": id_size,
        "attack": attack,
        "defense": defense,
        "stamina": stamina,
        "top_speed": top_speed,
        "dribble_accuracy": dribble_accuracy,
        "raw_block_data": block_data.hex()
    }

def write_player_data(file_path, player_info, new_attributes):
    block_offset = player_info["block_offset"]
    id_in_block_offset = player_info["id_in_block_offset"]
    id_size = player_info["id_size"]

    with open(file_path, 'r+b') as f:
        f.seek(block_offset)
        block_data = bytearray(f.read(64))

        # Update attributes (speculative offsets)
        if "attack" in new_attributes and 0x10 + 1 <= len(block_data):
            block_data[0x10:0x11] = struct.pack('<B', new_attributes["attack"])
        if "defense" in new_attributes and 0x11 + 1 <= len(block_data):
            block_data[0x11:0x12] = struct.pack('<B', new_attributes["defense"])
        if "stamina" in new_attributes and 0x12 + 1 <= len(block_data):
            block_data[0x12:0x13] = struct.pack('<B', new_attributes["stamina"])
        if "top_speed" in new_attributes and 0x13 + 1 <= len(block_data):
            block_data[0x13:0x14] = struct.pack('<B', new_attributes["top_speed"])
        if "dribble_accuracy" in new_attributes and 0x14 + 1 <= len(block_data):
            block_data[0x14:0x15] = struct.pack('<B', new_attributes["dribble_accuracy"])

        f.seek(block_offset)
        f.write(block_data)
    print(f"Dados do jogador {player_info['name']} (ID: {player_info['id']}) atualizados no offset 0x{block_offset:X}.")

if __name__ == '__main__':
    file_path = '/home/ubuntu/dt04_extracted_files/unnamed_0075.bin'
    csv_file_path = '/home/ubuntu/upload/Base_de_Dados_CSV_destruncado.csv'
    player_data_csv = load_player_data_from_csv(csv_file_path)

    # Exemplo de uso: Ler dados de um jogador
    player_id_to_read = 41188 # Júlio César
    player_info = read_player_data(file_path, player_id_to_read, player_data_csv)

    if player_info:
        print("--- Dados do Jogador Lidos ---")
        for key, value in player_info.items():
            print(f"{key}: {value}")

        # Exemplo de uso: Modificar e escrever dados de um jogador
        # Criar uma cópia do arquivo original para testes
        import shutil
        shutil.copy(file_path, file_path + ".bak")
        print(f"Backup criado em {file_path}.bak")

        new_attributes = {
            "attack": 99,
            "defense": 99,
            "stamina": 99,
            "top_speed": 99,
            "dribble_accuracy": 99
        }
        write_player_data(file_path, player_info, new_attributes)

        # Verificar se os dados foram atualizados corretamente
        updated_player_info = read_player_data(file_path, player_id_to_read, player_data_csv)
        if updated_player_info:
            print("\n--- Dados do Jogador Atualizados ---")
            for key, value in updated_player_info.items():
                print(f"{key}: {value}")

        # Restaurar o arquivo original (opcional, para manter a integridade)
        # shutil.copy(file_path + ".bak", file_path)
        # print(f"Arquivo original restaurado de {file_path}.bak")


