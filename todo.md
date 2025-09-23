## Tarefas Pendentes

- [x] Fase 1: Analisar repositório de referência e implementação existente
- [x] Fase 2: Análise do PESEditor.py e extração de funcionalidades relevantes
- [x] Fase 3: Implementação da leitura e manipulação do dt04.img
- [x] Fase 4: Aprofundar engenharia reversa do EDIT.bin para mapear atributos e nomes de jogadores
- [x] Fase 5: Reavaliar e refinar a engenharia reversa da estrutura de atributos e nomes do EDIT.bin
- [x] Fase 6: Investigar a relação entre Player_Edit.bin, PlayerAppearance.bin e EDIT.bin para nomes e atributos
  - [x] Analisar a estrutura do Player_Edit.bin para identificar nomes e atributos.
  - [x] Analisar a estrutura do PlayerAppearance.bin para identificar atributos de aparência.
  - [x] Correlacionar os dados encontrados nesses arquivos com o EDIT.bin.
  - [x] Entender como os IDs de jogadores no EDIT.bin se referem aos dados nesses outros arquivos.
- [x] Fase 7: Implementar modificação de atributos e edição de nomes de jogadores na ferramenta Python
  - [x] Integrar a lógica de leitura de atributos do `analyze_edit_bin_bit_structure_v19.py` no `pes_player_editor_v2.py`.
  - [x] Implementar a função `get_player_attributes` no `PESPlayerEditor`.
  - [x] Implementar a função `set_player_attributes` no `PESPlayerEditor`.
  - [ ] Continuar a investigação da estrutura de nomes para implementar `get_player_name` e `set_player_name`.
- [x] Fase 8: Refinar a lógica de identificação e edição de nomes de jogadores no EDIT.bin
  - [x] Análise aprofundada da estrutura de nomes e tentativa de correlação com IDs e strings extraídas.
  - [x] Conclusão: A estrutura de nomes é complexa e requer engenharia reversa mais aprofundada ou documentação específica, não sendo possível implementar de forma confiável no momento.
  - [ ] A função `get_player_name` e `set_player_name` serão implementadas com placeholders ou funcionalidade limitada, com base nas descobertas atuais, e a limitação será documentada.
- [x] Fase 9: Testar e validar as novas funcionalidades de modificação de jogadores
  - [x] Testar a leitura e escrita de atributos de jogadores.
  - [x] Validar o comportamento da edição de nomes (placeholder e aviso de limitação).
- [x] Fase 10: Atualizar documentação e manual do usuário
  - [x] Atualizar `manual_usuario_pes_editor.md` com as novas funcionalidades de edição de atributos e as limitações da edição de nomes.
  - [x] Atualizar `documentation_edit_img_relation.md` com as descobertas sobre a estrutura do EDIT.bin e a complexidade da edição de nomes.
- [ ] Fase 11: Entrega do sistema completo e documentação


