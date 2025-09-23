
import os
import struct

class PESPlayerEditor:
    def __init__(self, edit_bin_path, dt04_img_path):
        self.edit_bin_path = edit_bin_path
        self.dt04_img_path = dt04_img_path
        self.edit_bin_data = None
        self.dt04_files = {}

        self.load_edit_bin()
        self.load_dt04_img()

        # Definir a estrutura de atributos com base na análise v19
        self.attribute_structure = [
            # Atributos de 7 bits (0-99) - Valores comuns para habilidades
            ("Attack", 7),
            ("Defense", 7),
            ("Balance", 7),
            ("Stamina", 7),
            ("Top Speed", 7),
            ("Acceleration", 7),
            ("Response", 7),
            ("Agility", 7),
            ("Dribble Accuracy", 7),
            ("Dribble Speed", 7),
            ("Short Pass Accuracy", 7),
            ("Short Pass Speed", 7),
            ("Long Pass Accuracy", 7),
            ("Long Pass Speed", 7),
            ("Shot Accuracy", 7),
            ("Shot Power", 7),
            ("Shot Technique", 7),
            ("Free Kick Accuracy", 7),
            ("Swerve", 7),
            ("Heading", 7),
            ("Jump", 7),
            ("Technique", 7),
            ("Aggression", 7),
            ("Mentality", 7),
            ("Goalkeeping Skills", 7),
            ("Team Work", 7),
            # Atributos de 4 bits (Weak Foot Accuracy, Weak Foot Frequency, Form, Injury Resistance)
            ("Weak Foot Accuracy", 4),
            ("Weak Foot Frequency", 4),
            ("Form", 4),
            ("Injury Resistance", 4),
            # Posição Registrada (5 bits, 0-31)
            ("Registered Position", 5),
            # Consistência (2 bits)
            ("Consistency", 2),
            # Posições jogáveis (22 bits, 1 bit por posição)
            # Para simplificar, vamos agrupar como um bloco de bits por enquanto
            ("Playable Positions", 22),
            # Habilidades Especiais (30 bits, 1 bit por habilidade)
            # Para simplificar, vamos agrupar como um bloco de bits por enquanto
            ("Special Abilities", 30),
        ]
        self.player_block_size = 156 # Tamanho do bloco de dados de um jogador no EDIT.bin
        self.player_start_offset = 888 # Offset do primeiro jogador no EDIT.bin

    def load_edit_bin(self):
        if not os.path.exists(self.edit_bin_path):
            raise FileNotFoundError(f"EDIT.bin não encontrado em {self.edit_bin_path}")
        with open(self.edit_bin_path, 'rb') as f:
            self.edit_bin_data = bytearray(f.read())
        print("EDIT.bin carregado com sucesso.")

    def load_dt04_img(self):
        # Simplificação da leitura do dt04.img, para focar na edição
        # Em um caso real, usaria o PESDT04Reader
        print("Leitura do dt04.img ainda não implementada.")

    def _get_bit(self, data, bit_index):
        byte_index = bit_index // 8
        bit_offset_in_byte = bit_index % 8
        if byte_index >= len(data):
            return 0
        return (data[byte_index] >> bit_offset_in_byte) & 1

    def _read_value_from_bits_little_endian(self, data, start_bit, num_bits):
        value = 0
        for i in range(num_bits):
            if self._get_bit(data, start_bit + i):
                value |= (1 << i)
        return value

    def _write_value_to_bits_little_endian(self, data, start_bit, num_bits, new_value):
        # Limpar os bits existentes
        for i in range(num_bits):
            byte_index = (start_bit + i) // 8
            bit_offset_in_byte = (start_bit + i) % 8
            if byte_index < len(data):
                data[byte_index] &= ~(1 << bit_offset_in_byte) # Limpa o bit
        
        # Escrever o novo valor
        for i in range(num_bits):
            if (new_value >> i) & 1:
                byte_index = (start_bit + i) // 8
                bit_offset_in_byte = (start_bit + i) % 8
                if byte_index < len(data):
                    data[byte_index] |= (1 << bit_offset_in_byte) # Seta o bit

    def get_player_block(self, player_index):
        offset = self.player_start_offset + (player_index * self.player_block_size)
        if offset + self.player_block_size > len(self.edit_bin_data):
            return None
        return self.edit_bin_data[offset : offset + self.player_block_size]

    def set_player_block(self, player_index, new_block_data):
        offset = self.player_start_offset + (player_index * self.player_block_size)
        if offset + self.player_block_size > len(self.edit_bin_data):
            print(f"Erro: Bloco do jogador {player_index} fora dos limites do arquivo.")
            return False
        if len(new_block_data) != self.player_block_size:
            print(f"Erro: Novo bloco de dados tem tamanho incorreto para o jogador {player_index}.")
            return False
        self.edit_bin_data[offset : offset + self.player_block_size] = new_block_data
        return True

    def get_player_attributes(self, player_index):
        player_block = self.get_player_block(player_index)
        if player_block is None:
            return None

        attributes = {}
        current_bit_offset = 0

        for name, num_bits in self.attribute_structure:
            value = self._read_value_from_bits_little_endian(player_block, current_bit_offset, num_bits)
            attributes[name] = value
            current_bit_offset += num_bits
        
        return attributes

    def set_player_attributes(self, player_index, new_attributes):
        player_block = self.get_player_block(player_index)
        if player_block is None:
            return False

        temp_player_block = bytearray(player_block) # Trabalhar em uma cópia mutável
        current_bit_offset = 0

        for name, num_bits in self.attribute_structure:
            if name in new_attributes:
                new_value = new_attributes[name]
                # Validar o valor para o número de bits
                max_value = (1 << num_bits) - 1
                if not (0 <= new_value <= max_value):
                    print(f"Aviso: Valor {new_value} para {name} excede o limite de {max_value} para {num_bits} bits. Ignorando.")
                else:
                    self._write_value_to_bits_little_endian(temp_player_block, current_bit_offset, num_bits, new_value)
            current_bit_offset += num_bits
        
        return self.set_player_block(player_index, temp_player_block)

    def get_player_name(self, player_index):
        # A edição de nomes é complexa e não foi possível identificar a estrutura de forma confiável.
        # Retorna um placeholder e uma mensagem de aviso.
        print(f"Aviso: A estrutura de nomes no EDIT.bin não foi totalmente decifrada. Retornando nome placeholder para o jogador {player_index}.")
        return f"JOGADOR_{player_index}"

    def set_player_name(self, player_index, new_name):
        # A edição de nomes é complexa e não foi possível identificar a estrutura de forma confiável.
        # Esta função não fará alterações reais no arquivo EDIT.bin para nomes.
        print(f"Aviso: A estrutura de nomes no EDIT.bin não foi totalmente decifrada. Não é possível definir o nome para o jogador {player_index} como '{new_name}'.")

    def save_edit_bin(self, new_path=None):
        if new_path is None:
            new_path = self.edit_bin_path
        with open(new_path, 'wb') as f:
            f.write(self.edit_bin_data)
        print(f"EDIT.bin salvo em {new_path}")

if __name__ == '__main__':
    editor = PESPlayerEditor("/home/ubuntu/upload/EDIT.bin", "/home/ubuntu/upload/dt04.img")

    player_index_to_edit = 0 # O primeiro jogador no EDIT.bin

    # Exemplo de uso: Atributos
    print(f"\n--- Testando Atributos para Jogador {player_index_to_edit} ---")
    current_attributes = editor.get_player_attributes(player_index_to_edit)
    if current_attributes:
        print(f"Atributos atuais do jogador {player_index_to_edit}:")
        for attr, value in current_attributes.items():
            print(f"  {attr}: {value}")

        # Modificar alguns atributos
        new_attrs = {"Attack": 99, "Defense": 1, "Stamina": 95, "Top Speed": 90}
        print(f"\nTentando definir novos atributos: {new_attrs}")
        if editor.set_player_attributes(player_index_to_edit, new_attrs):
            print("Atributos definidos com sucesso.")
            updated_attributes = editor.get_player_attributes(player_index_to_edit)
            print(f"Atributos atualizados do jogador {player_index_to_edit}:")
            for attr, value in updated_attributes.items():
                print(f"  {attr}: {value}")
        else:
            print("Falha ao definir atributos.")

    # Exemplo de uso: Nomes (ainda não implementado de forma completa)
    print(f"\n--- Testando Nomes para Jogador {player_index_to_edit} ---")
    current_name = editor.get_player_name(player_index_to_edit)
    print(f"Nome atual do jogador {player_index_to_edit}: {current_name}")

    editor.set_player_name(player_index_to_edit, "Novo Nome Teste")

    editor.save_edit_bin("/home/ubuntu/EDIT_modificado_v2.bin")


