# Manual do Usuário - PES 2013 Player Editor

## Introdução

O **PES 2013 Player Editor** é uma ferramenta desenvolvida para modificar e adicionar jogadores diretamente nos arquivos do jogo Pro Evolution Soccer 2013. Esta ferramenta foi criada com base na análise do repositório `the4chancup/pes-db-generator` e permite a manipulação do arquivo `EDIT.bin` (Option File) do PES 2013.

## Características Principais

- **Análise do EDIT.bin**: Carrega e analisa a estrutura do arquivo Option File, incluindo a decodificação de atributos de jogadores.
- **Edição de Atributos de Jogadores**: Permite a modificação de atributos individuais de jogadores (velocidade, chute, passe, etc.) no EDIT.bin.
- **Sistema de backup**: Cria backups automáticos antes de qualquer modificação.
- **Validação de integridade**: Verifica a integridade dos arquivos antes e após modificações.
- **Backup em nuvem**: Sistema automatizado de backup para Supabase e GitLab.

## Arquivos Necessários

Para utilizar a ferramenta, você precisará dos seguintes arquivos:

1. **EDIT.bin** - Arquivo Option File do PES 2013
2. **Player_Edit_Base_19.bin** - Arquivo template para dados de jogadores
3. **PlayerAppearance_Base_16.bin** - Arquivo template para aparência de jogadores
4. **team_list.txt** - Lista de times e seus IDs

## Instalação e Configuração

### Pré-requisitos

- Python 3.7 ou superior
- Bibliotecas Python: `struct`, `os`, `shutil` (incluídas na instalação padrão)

### Estrutura de Diretórios

```
projeto/
├── pes_player_editor.py          # Ferramenta principal
├── test_pes_editor.py            # Script de testes
├── upload/
│   └── EDIT.bin                  # Arquivo Option File
├── generators/
│   ├── bin/
│   │   ├── Player_Edit_Base_19.bin
│   │   └── PlayerAppearance_Base_16.bin
│   └── team_list.txt
└── backups/                      # Diretório para backups locais
```

## Como Usar

### 1. Uso Básico

```python
from pes_player_editor_v2 import PESPlayerEditor

# Inicializar o editor
editor = PESPlayerEditor("/caminho/para/EDIT.bin", "/caminho/para/dt04.img")

# Exemplo de uso: Edição de Atributos
player_index_to_edit = 0 # O primeiro jogador no EDIT.bin

# Obter atributos atuais
current_attributes = editor.get_player_attributes(player_index_to_edit)
if current_attributes:
    print(f"Atributos atuais do jogador {player_index_to_edit}:\n{current_attributes}")

    # Modificar alguns atributos
    new_attrs = {"Attack": 99, "Defense": 1, "Stamina": 95, "Top Speed": 90}
    print(f"Tentando definir novos atributos: {new_attrs}")
    if editor.set_player_attributes(player_index_to_edit, new_attrs):
        print("Atributos definidos com sucesso.")
        updated_attributes = editor.get_player_attributes(player_index_to_edit)
        print(f"Atributos atualizados do jogador {player_index_to_edit}:\n{updated_attributes}")

# Exemplo de uso: Edição de Nomes (funcionalidade limitada)
current_name = editor.get_player_name(player_index_to_edit)
print(f"Nome atual do jogador {player_index_to_edit}: {current_name}")

editor.set_player_name(player_index_to_edit, "Novo Nome Teste")

# Salvar as alterações em um novo arquivo (ou sobrescrever o original)
editor.save_edit_bin("/caminho/para/EDIT_modificado.bin")
```

### 2. Executar Testes de Validação

```bash
python3 test_pes_editor.py
```

Este comando executará uma bateria completa de testes para verificar:
- Integridade dos arquivos necessários
- Funcionalidade de backup
- Análise do EDIT.bin
- Edição de atributos de jogadores
- Validação do comportamento da edição de nomes (placeholder e aviso de limitação)
- Sistemas de backup

## Funcionalidades Detalhadas

### Sistema de Backup

A ferramenta inclui um sistema robusto de backup:

**Backup Local:**
- Cria automaticamente um arquivo `.backup` antes de qualquer modificação
- Permite restaurar o estado original a qualquer momento

**Backup em Nuvem:**
- **Supabase**: Backup automático para armazenamento em nuvem
- **GitLab**: Versionamento e controle de mudanças

### Análise do EDIT.bin

A ferramenta analisa o arquivo EDIT.bin para:
- Identificar possíveis IDs de jogadores
- Mapear a estrutura interna do arquivo
- Localizar seções de dados de jogadores

### Geração de Dados de Jogadores

Baseado no algoritmo do repositório `the4chancup/pes-db-generator`, a ferramenta:
- Gera IDs únicos para jogadores baseados no time e posição
- Combina dados dos arquivos template
- Cria estruturas de dados compatíveis com o PES 2013

## Limitações Atuais

### Engenharia Reversa Incompleta

Devido à complexidade da estrutura proprietária do EDIT.bin, algumas funcionalidades ainda requerem desenvolvimento adicional:

1. **Nomes de Jogadores**: A localização e modificação dos nomes dos jogadores ainda não foi completamente implementada de forma confiável. A estrutura de nomes é complexa e requer engenharia reversa mais aprofundada ou documentação específica. Atualmente, a ferramenta fornece um placeholder para nomes e um aviso de limitação.

2. **Validação no Jogo**: Embora a ferramenta gere dados estruturalmente corretos, a validação completa no jogo requer testes adicionais.

### Funcionalidades Futuras

Para implementação completa, seria necessário:
- Mapeamento detalhado da estrutura do EDIT.bin
- Identificação dos offsets para cada atributo de jogador
- Sistema de validação de checksums (se aplicável)
- Interface gráfica para facilitar o uso

## Solução de Problemas

### Erro: "Arquivo não encontrado"
- Verifique se todos os arquivos necessários estão nos caminhos corretos
- Execute o teste de integridade: `python3 test_pes_editor.py`

### Erro: "Backup não pode ser criado"
- Verifique as permissões de escrita no diretório
- Certifique-se de que há espaço suficiente em disco

### Erro: "Nenhum ID de jogador encontrado"
- Verifique se o arquivo EDIT.bin é válido e não está corrompido
- Confirme que é um arquivo EDIT.bin do PES 2013

## Backup e Recuperação

### Restaurar Backup Local
```python
editor.restore_backup()
```

### Executar Backup em Nuvem
```bash
# Backup para Supabase
bash run_backup.sh

# Backup para GitLab
bash run_gitlab_backup.sh
```

## Considerações de Segurança

- **Sempre faça backup** antes de modificar arquivos do jogo
- **Teste em ambiente isolado** antes de usar em saves importantes
- **Mantenha cópias de segurança** dos arquivos originais do jogo

## Suporte e Desenvolvimento

Esta ferramenta foi desenvolvida como uma prova de conceito baseada na análise de arquivos do PES 2013. Para funcionalidades avançadas de modificação de jogadores, seria necessário:

1. Engenharia reversa mais profunda da estrutura do EDIT.bin
2. Documentação detalhada dos formatos de arquivo do PES 2013
3. Testes extensivos com diferentes versões do jogo

## Conclusão

O PES 2013 Player Editor fornece uma base sólida para modificação de arquivos do jogo, com sistema robusto de backup e análise estrutural. Embora algumas funcionalidades avançadas ainda estejam em desenvolvimento, a ferramenta demonstra a viabilidade de modificar dados de jogadores no PES 2013 de forma programática e segura.

