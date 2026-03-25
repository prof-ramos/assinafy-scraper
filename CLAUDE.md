# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Purpose

Este repositório contém a **documentação extraída da API Assinafy** em formato JSON estruturado, **testes E2E** para validar o funcionamento da API, e uma **CLI completa** para automação de assinaturas digitais.

## Comandos Comuns

### Instalação e Configuração

```bash
# Sincronizar dependências
uv sync

# Instalar CLI como comando do sistema
uv pip install -e .
```

### Testes

```bash
# Testes unitários
.venv/bin/python -m pytest tests/ -v

# Testes com cobertura
.venv/bin/python -m pytest tests/ --cov=assinafy --cov-report=term-missing

# Testes E2E (validam API real)
.venv/bin/python test_e2e.py
```

### CLI (Nova)

```bash
# Usar CLI
assinafy automate documento.pdf --email user@example.com --name "User Name"
assinafy upload documento.pdf
assinafy send-link DOCUMENT_ID --email user@example.com

# Verbosidade (-v=INFO, -vv=DEBUG)
assinafy -vv upload documento.pdf

# Config customizada
assinafy -c config/custom.yaml upload documento.pdf
```

### Linting e Formatação

```bash
# Linting
.venv/bin/python -m ruff check assinafy/

# Formatar código
.venv/bin/python -m black assinafy/
```

## Arquitetura do Sistema

### Estrutura Modular

O projeto está organizado em 3 camadas:

1. **CLI Layer** (`assinafy/cli.py` + `assinafy_cli.py`)
   - Interface Click para comandos de automação
   - Suporta verbosidade e configuração customizada

2. **Business Logic** (`assinafy/api/`, `assinafy/automation/`)
   - `api/client.py`: Cliente HTTP reutilizável com session management
   - `api/documents.py`: Operações de documentos (upload, get, wait, list)
   - `automation/signature.py`: Orquestrador do fluxo completo de assinatura
   - `automation/email.py`: Envio de emails com mailto links

3. **Infrastructure** (`assinafy/config.py`, `assinafy/logging_config.py`)
   - Sistema de configuração multi-source (env vars > YAML > defaults)
   - Logging estruturado com formatters customizados

### Fluxo de Dados

```
CLI Command
  ↓
Config.load()  # Carrega config de YAML + .env
  ↓
Business Logic (automation/signature.py)
  ↓
API Client (api/client.py + api/documents.py)
  ↓
Assinafy API
```

### Configuração

**Precedência** (maior prioridade primeiro):
1. Variáveis de ambiente (`ASSINAFY_API_KEY`, `ASSINAFY_WORKSPACE_ID`)
2. Arquivo YAML (`config/*.yaml`)
3. Defaults hardcoded

**Arquivo `.env`** (credenciais sensíveis):
```bash
ASSINAFY_API_KEY=sua_chave
ASSINAFY_WORKSPACE_ID=seu_workspace_id
```

**Arquivo YAML** opcional (configurações não-sensíveis):
```yaml
assinafy:
  base_url: "https://api.assinafy.com.br/v1"
  document_ready_timeout: 60
  polling_interval: 2
```

## CLI Assinafy

### Comandos Disponíveis

**`automate`** - Fluxo completo de assinatura:
```bash
assinafy automate documento.pdf -e user@example.com -n "User"
```

**`upload`** - Upload de PDF:
```bash
assinafy upload documento.pdf
```

**`send-link`** - Enviar link para documento existente:
```bash
assinafy send-link DOCUMENT_ID -e user@example.com
```

### Verbosidade

- Sem flag: WARNING (apenas erros)
- `-v`: INFO (progresso)
- `-vv`: DEBUG (detalhes técnicos)

## Scripts Legados (Compatibilidade)

Todos os scripts legados continuam funcionando e usam logging estruturado:

- `automatizar_assinatura.py` - Automação completa (hardcoded params)
- `test_upload_pdf.py` - Upload isolado de PDF
- `enviar_link_assinatura.py` - Enviar link existente

**Nota**: Preferir a nova CLI `assinafy` para desenvolvimento futuro.

## Testes

### Estrutura de Testes

```
tests/
├── conftest.py          # Fixtures compartilhadas
├── test_cli.py          # Testes CLI (8 testes)
├── test_config.py       # Testes config (6 testes)
└── test_logging.py      # Testes logging (7 testes)
```

### Executar Teste Específico

```bash
# Teste específico
.venv/bin/python -m pytest tests/test_config.py::TestAssinafyConfig::test_direct_instantiation -v

# Testes de um módulo
.venv/bin/python -m pytest tests/test_cli.py -v

# Testes com falhas
.venv/bin/python -m pytest tests/ -v --tb=short
```

### Testes E2E

**Arquivo**: `test_e2e.py`

Valida funcionamento real da API Assinafy:
- Autenticação, listagem de recursos
- Validação de formato de resposta
- Paginação e busca full-text

**Resultado esperado**: 9/9 testes passando (100%)

## Documentação da API Assinafy

**Arquivo**: `data/assinafy_api.json` (186KB)

- 84 endpoints documentados
- 10 seções organizadas (Signer, Document, Template, Webhooks, etc.)
- Base URL: `https://api.assinafy.com.br/v1`

**Consultar via jq**:
```bash
cat data/assinafy_api.json | jq '.sections[] | {title: .title, endpoints: (.endpoints | length)}'
```

## Headers de Autenticação

```
X-Api-Key: <ASSINAFY_API_KEY>
Content-Type: application/json  # OMITIR para uploads multipart
Accept: application/json
```

**Importante**: Para uploads de arquivo, **não incluir** `Content-Type` header - requests define automaticamente para `multipart/form-data`.

## Detalhes de Implementação

### Multipart Upload Bug (FIXED)

**Problema**: Session com `Content-Type: application/json` interfere com uploads multipart.

**Solução**: `AssinafyClient` inicializado sem Content-Type por padrão:
```python
# assinafy/api/client.py
self.session.headers.update(config.get_auth_headers(include_content_type=False))
```

Para uploads, usar método `upload_file()` que define apenas `X-Api-Key`.

### Logging Estruturado

**Formato**: `[TIMESTAMP] LEVEL [module:line] message`

**Uso**:
```python
from assinafy.logging_config import setup_logging, get_logger

logger = get_logger(__name__)
logger.info("Progress update")
logger.debug("Technical details")
```

**Scripts legados**: Prints mantidos apenas para output final de dados (document_id, signing_url).

## Documentação Adicional

- **`docs/migracao_cli.md`** - Guia de migração scripts → CLI
- **`docs/resumo_fases_4_6.md`** - Resumo implementação CLI/config/logging
- **`docs/arquitetura.md`** - Arquitetura completa com diagramas
- **`docs/fluxo_documentos_assinafy.md`** - Análise fluxo de documentos

## Dependências

**Runtime**:
- `requests>=2.31.0` - Cliente HTTP
- `python-dotenv>=1.0.0` - Variáveis de ambiente
- `click>=8.1.0` - Framework CLI
- `pyyaml>=6.0.0` - Config YAML

**Dev**:
- `pytest>=7.4.0` - Testes
- `pytest-cov>=4.1.0` - Cobertura
- `black>=23.0.0` - Formatação
- `ruff>=0.1.0` - Linting

## Adicionar Novos Comandos CLI

1. Adicionar função em `assinafy/cli.py`:
```python
@cli.command()
@click.argument("param")
@click.pass_context
def new_command(ctx, param):
    """Descrição do comando"""
    config = ctx.obj["config"]
    # Lógica aqui
```

2. Testar com Click:
```python
# tests/test_cli.py
def test_new_command_help(self, runner):
    result = runner.invoke(cli, ["new-command", "--help"])
    assert result.exit_code == 0
```

## Status de Documentos API

Documentos passam por estes status:
```
uploading → uploaded → metadata_processing → metadata_ready → pending_signature → certificated
```

**`signing_url` disponível imediatamente** após upload - não aguardar processamento.
