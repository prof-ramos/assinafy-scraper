# Assinafy API Documentation Scraper

Scraper para extrair automaticamente a documentação da API Assinafy (https://api.assinafy.com.br/v1/docs) e gerar um JSON estruturado.

## Funcionalidades

- Extrai endpoints, parâmetros e exemplos da documentação HTML
- Parse comandos curl para identificar métodos HTTP e paths
- Organiza endpoints por seções (Authentication, Signer, Document, etc.)
- Gera JSON estruturado pronto para uso
- Suporte a execução via CLI ou script cmux

## Instalação

```bash
# Instalar dependências
uv sync
```

## Uso

### Via CLI

```bash
# Scrape completo (salva em data/assinafy_api.json)
uv run python -m src.cli scrape

# Scrape com caminho customizado
uv run python -m src.cli scrape -o ~/Documents/assinafy.json

# Informações sobre o JSON gerado
uv run python -m src.cli info
```

### Via script wrapper

```bash
# Usar o wrapper executável
./assinafy scrape
./assinafy info
```

### Via entry points instalados

Após `uv sync`, os seguintes comandos ficam disponíveis:

```bash
assinafy-scrape        # Equivalente a: uv run python -m src.cli scrape
assinafy-info          # Equivalente a: uv run python -m src.cli info
```

### Via script cmux

```bash
# Executa scrape com progress bar e logs
./scripts/scrape_cmux.sh
```

## Estrutura do Projeto

```
assinafy-scraper/
├── pyproject.toml          # Dependências
├── src/
│   ├── scraper/           # Lógica de scraping
│   │   ├── base.py        # AssinafyScraper (fetch HTML)
│   │   ├── parsers.py     # DocumentationParser (parse HTML)
│   │   ├── models.py      # Pydantic models
│   │   └── extractor.py   # DocumentationExtractor (orchestrator)
│   ├── output/            # Export
│   │   └── json_writer.py # JSONWriter
│   └── cli.py             # CLI com Click
├── scripts/
│   └── scrape_cmux.sh     # Script cmux
└── data/                  # Arquivos gerados
    └── assinafy_api.json  # JSON estruturado
```

## Formato de Saída

O JSON gerado contém:

```json
{
  "base_url": "https://api.assinafy.com.br/v1",
  "extracted_at": "2026-03-24T10:00:00",
  "metadata": {
    "source": "html_scraping",
    "pages_scraped": 1,
    "total_endpoints": 20
  },
  "sections": [
    {
      "title": "Authentication",
      "level": 1,
      "endpoints": [
        {
          "title": "Create API Key",
          "method": "POST",
          "path": "/v1/auth/api-keys",
          "parameters": [...],
          "request_example": {...},
          "response_example": {...},
          "requires_auth": true,
          "supports_pagination": false
        }
      ]
    }
  ]
}
```

## Desenvolvimento

```bash
# Executar com debug
uv run python -m src.cli scrape

# Verificar JSON
cat data/assinafy_api.json | jq '.sections | length'
cat data/assinafy_api.json | jq '.sections[].endpoints | length'
```

## Requisitos

- Python 3.9+
- uv (package manager)
- Conexão com internet

## Dependências

- requests >= 2.31.0
- beautifulsoup4 >= 4.12.0
- pydantic >= 2.0.0
- click >= 8.1.0
- lxml >= 4.9.0
