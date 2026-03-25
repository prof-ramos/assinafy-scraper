# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Scraper que extrai a documentação da API Assinafy (https://api.assinafy.com.br/v1/docs) e gera um JSON estruturado. A documentação é HTML estático, então não requer browser automation.

## Commands

### Setup
```bash
uv sync                    # Install dependencies
```

### Run
```bash
uv run python -m src.cli scrape        # Scrape completo
uv run python -m src.cli scrape -o <path>  # Output customizado
uv run python -m src.cli info          # Informações sobre JSON gerado
./assinafy scrape                      # Via wrapper
./scripts/scrape_cmux.sh               # Via cmux (com progress bar)
```

### Development
```bash
uv run python -m src.cli scrape        # Executar scraper
cat data/assinafy_api.json | jq '.'    # Ver JSON gerado
```

## Architecture

O projeto segue um fluxo de dados linear em 3 camadas:

```
HTML → Parser → Models → Output
```

### Componentes

**1. Scraper Base** (`src/scraper/base.py`)
- `AssinafyScraper`: Fetch HTML das páginas usando requests
- Primeiro tenta `/openapi.json`, `/swagger.json` - se encontrar, usa parse direto
- Senão, faz scraping de `/docs` e subpáginas

**2. HTML Parser** (`src/scraper/parsers.py`)
- `DocumentationParser`: Extrai informações do HTML com BeautifulSoup + lxml
- `extract_sections()`: Detecta h1/h2/h3 e agrupa conteúdo
- `_parse_curl_command()`: Regex para extrair método HTTP, path, headers, body de comandos curl
- `extract_parameter_tables()`: Parse tabelas de parâmetros
- `extract_endpoints()`: Combina curl blocks + tabelas → objetos Endpoint

**3. Models** (`src/scraper/models.py`)
- Pydantic models com validação: `Endpoint`, `Section`, `Parameter`, `Documentation`
- `Endpoint.normalize_path()`: Substitui IDs por placeholders (MongoDB IDs, UUIDs, numéricos)
- `Documentation.get_all_endpoints()`: Flatten todos os endpoints

**4. Orchestrator** (`src/scraper/extractor.py`)
- `DocumentationExtractor`: Coordena o fluxo completo
- `extract()`: fetch → parse → organize → return Documentation
- `_organize_sections()`: Associa endpoints às seções baseado no path

**5. Output** (`src/output/json_writer.py`)
- `JSONWriter`: Converte models Pydantic → JSON estruturado

### Fluxo de Dados

```
DocumentationExtractor.extract()
  ↓
AssinafyScraper.fetch_all_pages()
  ├─→ check_openapi_spec() → OpenAPI? → _parse_openapi()
  └─→ fetch_documentation() → HTML pages
       ↓
  DocumentationParser(html)
    ├─→ extract_sections() → Section[]
    ├─→ extract_curl_blocks() → _parse_curl_command() → Endpoint[]
    └─→ extract_parameter_tables() → Parameter[]
       ↓
  _organize_sections() → associa endpoints às seções
       ↓
  Documentation (Pydantic model)
       ↓
  JSONWriter.write() → data/assinafy_api.json
```

## Patterns Importantes

### Parse de Comandos Curl
O scraper confia em blocos de código curl na documentação. Regex em `_parse_curl_command()` extrai:
- Método: `-X (GET|POST|PUT|DELETE)`
- URL: `"https://api.assinafy.com.br/v1([^"]+)"`
- Headers: `-H "Key: Value"`
- Body: `-d "{...}"`

### Normalização de Paths
`Endpoint.normalize_path()` substitui IDs por placeholders:
- MongoDB IDs (24 hex chars): `/abc123...` → `/{id}`
- UUIDs: `/123e4567-e89b-12d3-a456-426614174000` → `/{uuid}`
- Numéricos (4+ digits): `/1234` → `/{id}`

### Detecção de Autenticação
Endpoint `requires_auth = True` se tiver parâmetros:
- `X-Api-Key` (header)
- `Authorization: Bearer {token}` (header)

### Organização de Seções
`_organize_sections()` associa endpoints às seções usando matching de string:
- Se endpoint path contém nome da seção (case insensitive)
- Ex: `/accounts/123/signers` → seção "Signer"
- Endpoints sem match → seção root

## Convenções

- **Package manager**: Sempre usar `uv` (nunca `pip` direto)
- **Imports absolutos**: `from src.scraper.X import Y` (não relative imports)
- **Pydantic v2**: Usar field defaults com `Field(default_factory=...)` para mutables
- **HTML Parser**: lxml (não html.parser) - mais rápido
- **Line length**: 100 caracteres (ruff/black config)
