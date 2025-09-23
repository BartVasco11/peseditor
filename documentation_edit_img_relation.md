# Documentação: Relação entre EDIT.bin e Arquivos .img no PES 2013

## Introdução

Este documento detalha a relação entre o arquivo `EDIT.bin` e os arquivos `.img` (especialmente `dt04.img` e `dt0f.img`) no Pro Evolution Soccer 2013, com foco na modificação de dados de jogadores. A análise foi baseada em engenharia reversa de arquivos do jogo e na exploração de um repositório de referência (`the4chancup/pes-db-generator`).

## Análise do `player_edit.py` e Arquivos Base

O script `player_edit.py` do repositório `the4chancup/pes-db-generator` é uma ferramenta para gerar dados de jogadores. Ele utiliza os seguintes arquivos como base:

*   `PlayerEdit_Base_19.bin`: Este arquivo serve como um modelo para os dados de edição de jogadores.
*   `PlayerAppearance_Base_16.bin`: Este arquivo serve como um modelo para os dados de aparência dos jogadores.
*   `team_list.txt`: Contém uma lista de IDs de times e seus respectivos nomes/abreviações, utilizados para gerar IDs de jogadores.

A lógica do script `player_edit.py` envolve a construção de `player_id`s a partir de `team_id` e um índice de jogador. Ele então empacota esses IDs com seções dos arquivos `PlayerEdit_Base_19.bin` e `PlayerAppearance_Base_16.bin` para criar um novo arquivo `Player_Edit.bin`.

### Estrutura dos Arquivos Base (`PlayerEdit_Base_19.bin` e `PlayerAppearance_Base_16.bin`)

Ambos os arquivos binários base (`PlayerEdit_Base_19.bin` e `PlayerAppearance_Base_16.bin`) começam com dois DWORDs (4 bytes cada) que representam o `player_id`. Por exemplo, o `PlayerEdit_Base_19.bin` tem 116 bytes e o `PlayerAppearance_Base_16.bin` tem 60 bytes. O restante dos bytes nesses arquivos contém dados binários que, presumivelmente, codificam os atributos e características dos jogadores. A análise detalhada desses blocos binários é complexa e exigiria mais engenharia reversa para mapear cada campo a um atributo específico do jogador (como chute, passe, velocidade, etc.).

## Relação com `EDIT.bin`

O `EDIT.bin` é o arquivo Option File do PES 2013, responsável por armazenar as modificações feitas pelo usuário nos jogadores, times e outras configurações do jogo. A análise aprofundada do `EDIT.bin` revelou a presença de IDs de jogadores e blocos de dados que correspondem a registros de jogadores. Conseguimos mapear e implementar com sucesso a leitura e escrita de **atributos de jogadores** (como ataque, defesa, velocidade, etc.) dentro desses blocos, utilizando uma abordagem de leitura e escrita de bits.

No entanto, a **edição de nomes de jogadores** no `EDIT.bin` provou ser mais complexa. As tentativas de identificar uma tabela de nomes clara ou de decodificar nomes diretamente dos blocos de jogadores não foram conclusivas. Isso sugere que os nomes são referenciados por um mecanismo mais elaborado (por exemplo, IDs que apontam para uma tabela de strings em outra parte do arquivo ou em um arquivo externo, ou uma codificação específica que não foi desvendada). Atualmente, a ferramenta fornece um placeholder para nomes e um aviso de limitação para esta funcionalidade.

Isso confirma que o `EDIT.bin` contém os dados de jogadores de forma direta, e a ferramenta desenvolvida fornece uma maneira programática de modificar esses dados, especialmente os atributos. A estrutura interna do `EDIT.bin` é proprietária e complexa, mas a engenharia reversa dos atributos foi bem-sucedida.

## Relação com Arquivos `.img` (`dt04.img`, `dt0f.img`)

Os arquivos `.img` são arquivos AFS (Advanced File System) que contêm diversos recursos do jogo, incluindo modelos, texturas, áudios e, potencialmente, dados de jogadores. Inicialmente, focamos na engenharia reversa do `dt04.img` e `dt0f.img`.

*   **`dt04.img`**: Contém dados de jogadores e atributos. Análises anteriores identificaram blocos de IDs de jogadores, mas a correlação com nomes e atributos específicos foi desafiadora.
*   **`dt0f.img`**: Acreditava-se que continha dados de estatísticas de jogadores, especificamente nos arquivos `unnamed_1974.bin` e `unnamed_1975.bin`. No entanto, a extração desses arquivos revelou que eles estão vazios (tamanho 0 bytes). Isso indica que, para o PES 2013, esses arquivos específicos dentro do `dt0f.img` não contêm os dados de jogadores que procuramos, ou que a forma como são acessados ou preenchidos é diferente do esperado.

### Conclusão sobre a Relação

A relação entre `EDIT.bin` e os arquivos `.img` parece ser a seguinte:

1.  **`EDIT.bin`**: É o principal arquivo para modificação de dados de jogadores, contendo os atributos editáveis. As ferramentas como o `pes-db-generator` visam gerar dados para serem inseridos diretamente neste arquivo (ou em sua versão decriptada).
2.  **Arquivos `.img` (`dt04.img`, `dt0f.img`)**: Podem conter dados base de jogadores ou outros recursos relacionados, mas a modificação direta de jogadores parece ser feita primariamente através do `EDIT.bin`. Os arquivos `unnamed_1974.bin` e `unnamed_1975.bin` no `dt0f.img` não são a fonte direta de dados de jogadores para modificação, como inicialmente pensado.

É provável que os arquivos `.img` contenham dados de jogadores que são carregados pelo jogo, e o `EDIT.bin` sobrescreve ou complementa esses dados com as modificações do usuário. A ausência de dados nos `unnamed_1974.bin` e `unnamed_1975.bin` reforça a ideia de que o `EDIT.bin` é o foco principal para a modificação de jogadores.

## Próximos Passos

Com base nesta documentação, os próximos passos devem se concentrar em:

1.  Aprofundar a engenharia reversa da estrutura do `EDIT.bin` para mapear os atributos dos jogadores.
2.  Utilizar os insights do `player_edit.py` e dos arquivos base para desenvolver uma ferramenta Python para ler, modificar e escrever dados de jogadores no `EDIT.bin`.

