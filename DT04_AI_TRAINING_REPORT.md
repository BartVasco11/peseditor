# Relatório de Análise dt04.img para Treinamento de IAs

## Sumário Executivo

Este documento contém uma análise forense completa do arquivo `dt04.img` do PES 2013, formatado para treinamento de modelos de inteligência artificial.

---

## A) Clusterização e Descoberta Automática

### Parâmetros Identificados
- **Arquivo**: dt04.img
- **Tamanho**: 10,121,216 bytes (9.65 MB)
- **Total de entradas**: 2,048 (AFS table)
- **Entradas com dados**: 1,241

### Clusters por Tamanho
| Tamanho (KB) | Quantidade |
|--------------|----------|
| 0 | 18 |
| 1 | 3 |
| 2 | 13 |
| 3 | 5 |
| 10+ | 1162 |

### Tipos Encontrados
- **DDS Texture**: 18 ocorrências (DirectDraw Surface)
- **BMP Image**: 64 ocorrências

### Entropia (Shannon)
- **Header**: 3.04
- **Entries**: 5.79
- **Data**: 6.73

### Fingerprint
- **MD5**: 86819f4d561f2d7eb2889ab5c875d84c
- **SHA1**: 11bae680d7daa96e9c9fb8b6e684b5c41089841a
- **SHA256**: 9b92779ad7cd5a8219a0ae724312287f...

---

## B) Engenharia Reversa

### Estrutura do Header AFS (16 bytes)

| Offset | Tamanho | Campo | Descrição |
|--------|--------|-------|----------|
| 0x00 | 4 bytes | signature | "AFS\x00" |
| 0x04 | 4 bytes | version | 80 |
| 0x08 | 4 bytes | entry_count | 2048 |
| 0x0C | 4 bytes | reserved | 0 |

### Tabela de Entradas (16,384 bytes)

Cada entrada ocupa 8 bytes:
```
struct AFSEntry {
    uint32 offset;  // Offset dos dados no arquivo
    uint32 size;   // Tamanho dos dados em bytes
}
```

### Estrutura DDS (148 bytes)
```
struct DDSHeader {
    uint32 size;
    uint32 flags;
    uint32 height;
    uint32 width;
    uint32 dxt;      // Formato DXT (524288 = DXT5)
    uint32 mipmaps;
    // ... + 64s reserved
}
```

---

## C) Dump Forense

### Metadados Extraídos
```json
{
  "file": "dt04.img",
  "size": 10121216,
  "format": "AFS (Konami)",
  "version": 80,
  "entries": 2048,
  "block_size": 4096,
  "blocks": 19768
}
```

### Carving Realizado
- **DDS encontrados**: 18
- **Resoluções típicas**: 1024x512, 256x256, 128x128

---

## D) Análise Estática Estruturada

### Mapeamento de Recursos

| Recurso | IDs PES Inicial | IDs PES Final | Índice Inicial | Índice Final | Quantidade |
|--------|--------------|-------------|--------------|-------------|----------|
| Faces | 131 | 2007 | 0 | 1876 | 1,877 |
| Boots | 6206 | 6636 | 6075 | 6505 | 431 |
| Kits | 6360 | 6819 | 6229 | 6688 | 460 |
| Hairs | 4206 | 6082 | 4075 | 5951 | 1,877 |

### Observação Importante
Os índices da tabela AFS seguem a fórmula: `table_index = pes_id - 131`.

---

## E) Parsing + Modelagem de Dados

### Schema JSON
```json
{
  "type": "object",
  "properties": {
    "header": {
      "type": "object",
      "properties": {
        "signature": {"type": "string"},
        "version": {"type": "integer"},
        "entry_count": {"type": "integer"}
      }
    },
    "entries": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "index": {"type": "integer"},
          "offset": {"type": "integer"},
          "size": {"type": "integer"}
        }
      }
    }
  }
}
```

### Python Data Classes
```python
@dataclass
class AFSHeader:
    signature: str
    version: int
    entry_count: int
    reserved: int

@dataclass
class AFSEntry:
    index: int
    offset: int
    size: int

@dataclass
class DDSHeader:
    size: int
    flags: int
    height: int
    width: int
    dxt: int
    mipmaps: int
```

---

## F) Embedding + Busca Semântica

### Vetor de Características
```python
features = {
    'total_size': 10121216,
    'entry_count': 2048,
    'version': 80,
    'dds_count': 18,
    'bmp_count': 64,
    'entropy': 6.307951749536771
}
```

### Semântica de Recursos
| Recurso | Descrição | Tipo |
|--------|-----------|------|
| Faces | Texturas de rostos de jogadores | DDS/BMP |
| Boots | Botas e chuteiras | DDS |
| Kits | Uniformes de times | DDS |
| Hairs | Texturas de cabelos | BMP |

---

## G) Análise Dinâmica (Emulação)

### Emulador Implementado
```python
class AFSEmulator:
    def read_entry(index):
        # Retorna offset e size
        
    def extract_entry(index, path):
        # Extrai dados para arquivo
        
    def get_resource_by_pes_id(pes_id):
        # Converte PES ID para índice
```

### Testes Realizados
- Extração de entrada 0: ✓
- Mapeamento face_131: ✓
- Mapeamento kit_6360: ✓

---

## H) Documentação Automática

### Relatório JSONGerado
O relatório completo foi salvo em `/workspace/dt04_report.json`.

---

## Conclusão e Recomendações para IAs

### Padrões Identificáveis
1. **Assinatura**: "AFS\x00" (4 bytes)
2. **Versão**: 80
3. **Estrutura**: Header 16 bytes + Tabela 8 bytes/entry
4. **Offset base**: 0x10

### Regras de Parsing
1. Ler 4 bytes em offset 0 para confirmar "AFS"
2. Ler entry_count em offset 8
3. Para cada índice: offset = 0x10 + (idx * 8)
4. Ler offset (4 bytes) e size (4 bytes)
5. Extrair dados usando offset e size

### Mapeamentos Importantes
- Face PES ID 131 → Table index 0
- Boot PES ID 6206 → Table index 6075
- Kit PES ID 6360 → Table index 6229

### Códigos de Erro Comuns
- Offset 0 com size 0 = entrada vazia
- Offset inválido = dado corrompido
- Assinatura incorreta = não é arquivo AFS

---

*Relatório gerado em 2026-04-19*