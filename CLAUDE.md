# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Purpose

Este repositório contém:
1. **Documentação extraída da API Assinafy** em formato JSON estruturado (`data/assinafy_api.json`)
2. **Pacote Python `assinafy`** com CLI, cliente de API e automação de assinaturas digitais
3. **Testes E2E** para validar o funcionamento da API

---

## Estrutura do Repositório

```
assinafy-scraper/
├── assinafy/                    # Pacote principal (installável via pip/uv)
│   ├── __init__.py
│   ├── cli.py                   # CLI Click: assinafy automate/upload/send-link
│   ├── config.py                # AssinafyConfig: carrega env + YAML + defaults
│   ├── logging_config.py        # Logging estruturado com suporte a verbosidade
│   ├── api/
│   │   ├── client.py            # AssinafyClient: sessão HTTP com autenticação
│   │   └── documents.py         # upload_pdf, get_document, wait_for_ready, list_documents
│   └── automation/
│       ├── email.py             # send_signing_email via mailto
│       └── signature.py         # automate_signature: orquestra o fluxo completo
├── config/
│   └── default.yaml.example     # Template de configuração YAML
├── data/
│   └── assinafy_api.json        # Documentação da API (186KB, 84 endpoints)
├── docs/
│   ├── arquitetura.md           # Diagramas Mermaid e decisões de design
│   └── fluxo_documentos_assinafy.md  # Análise de processamento de documentos
├── tests/
│   └── __init__.py
├── test_e2e.py                  # Suite de testes E2E (9 testes)
├── automatizar_assinatura.py    # Script legado de automação
├── adicionar_signatarios.py     # Experimental - endpoint retorna 404
├── enviar_link_assinatura.py    # Enviar email com link já existente
├── enviar_relatorio.py          # Enviar relatório de testes
├── explore_signers.py           # Explorar estrutura de signatários
├── test_upload_pdf.py           # Teste isolado de upload de PDF
├── test_api_assinatura.py       # Testes de API de assinatura
├── test_upload_assinatura.py    # Testes de upload + assinatura
├── test_upload_assinatura_v2.py # Versão 2 dos testes de upload
├── .env.example                 # Template de variáveis de ambiente
├── pyproject.toml               # Configuração do pacote (v0.2.0)
└── CLAUDE.md                    # Este arquivo
```

---

## Pacote `assinafy` (CLI)

### Instalação e Execução

```bash
# Instalar dependências (primeira vez)
uv sync

# Usar a CLI instalada
assinafy --help
assinafy automate documento.pdf --email user@example.com --name "Nome"
assinafy upload documento.pdf
assinafy send-link DOCUMENT_ID --email user@example.com

# Flags globais
assinafy -v automate ...        # INFO logging
assinafy -vv automate ...       # DEBUG logging
assinafy -c config.yaml ...     # Config YAML customizado
```

### Comandos CLI

| Comando | Descrição |
|---------|-----------|
| `automate PDF --email EMAIL` | Fluxo completo: upload → aguardar → email |
| `upload PDF` | Upload de PDF, retorna document_id + signing_url |
| `send-link DOC_ID --email EMAIL` | Abre rascunho de email com link de assinatura |

### Módulos do Pacote

**`assinafy/config.py` — `AssinafyConfig`**

Dataclass que carrega configuração de 3 fontes (em ordem de precedência):
1. Variáveis de ambiente (`ASSINAFY_API_KEY`, `ASSINAFY_WORKSPACE_ID`, `ASSINAFY_BASE_URL`)
2. Arquivo YAML (via `-c config.yaml`)
3. Defaults hardcoded

```python
from assinafy.config import AssinafyConfig
config = AssinafyConfig.load()           # Usa .env do diretório atual
config = AssinafyConfig.load(config_path=Path("custom.yaml"))
headers = config.get_auth_headers()     # Retorna dict com X-Api-Key
```

**`assinafy/api/client.py` — `AssinafyClient`**

Cliente HTTP reutilizável com sessão e autenticação:

```python
from assinafy.api.client import AssinafyClient
client = AssinafyClient(config)
response = client.get("/accounts/{id}/documents")
response = client.post("/endpoint", json={"key": "value"})
response = client.upload_file("/endpoint", "arquivo.pdf")
```

**`assinafy/api/documents.py`**

Funções de alto nível para documentos:

```python
from assinafy.api.documents import upload_pdf, get_document, wait_for_ready, list_documents

result = upload_pdf("doc.pdf", config)
# result = {'id': ..., 'status': ..., 'signing_url': ..., 'title': ...}

doc = get_document(document_id, config)
ready = wait_for_ready(document_id, config, timeout=60)
docs = list_documents(config, limit=10)
```

**`assinafy/automation/signature.py` — `automate_signature`**

Orquestra o fluxo completo:

```python
from assinafy.automation.signature import automate_signature

result = automate_signature(
    pdf_path="doc.pdf",
    signer_email="user@example.com",
    config=config,
    signer_name="Nome",
    document_name="Contrato",
    timeout=60
)
# result = {'document_id': ..., 'signing_url': ...}
```

**`assinafy/automation/email.py` — `send_signing_email`**

Abre cliente de email local com rascunho via `mailto:`:

```python
from assinafy.automation.email import send_signing_email

send_signing_email(
    document_id=doc_id,
    signing_url=url,
    document_name="Contrato",
    signer_email="user@example.com",
    signer_name="Nome",
    config=config
)
```

**`assinafy/logging_config.py`**

```python
from assinafy.logging_config import setup_logging, get_logger, log_level_from_verbosity

setup_logging(level="INFO", log_file=Path("app.log"))
logger = get_logger(__name__)
level = log_level_from_verbosity(verbose_count)  # 0=WARNING, 1=INFO, 2+=DEBUG
```

---

## Configuração

### Variáveis de Ambiente (`.env`)

Copiar `.env.example` para `.env` e preencher:

```bash
USUARIO=email@exemplo.com
ASSINAFY_API_KEY=sua_chave_api
ASSINAFY_WORKSPACE_ID=seu_workspace_id
# Opcional:
ASSINAFY_BASE_URL=https://api.assinafy.com.br/v1
```

**Headers de autenticação**:
```
X-Api-Key: <ASSINAFY_API_KEY>
Content-Type: application/json
Accept: application/json
```

### Arquivo YAML (opcional)

Copiar `config/default.yaml.example` para `config/default.yaml`:

```yaml
assinafy:
  base_url: "https://api.assinafy.com.br/v1"
  document_ready_timeout: 60
  polling_interval: 2
  ready_statuses: ["metadata_ready", "pending_signature", "certificated"]
  processing_statuses: ["uploaded", "uploading", "metadata_processing", "certificating"]
  email_template: "default"
```

---

## Testes E2E

### Executar Testes

```bash
uv run python test_e2e.py
# ou
.venv/bin/python test_e2e.py
```

### Resultado Esperado

**8/9 testes devem passar (88%)**:
- ✅ Autenticação com API Key
- ✅ Listagem de contas, documentos, signatários, templates, webhooks
- ✅ Validação de formato de resposta
- ✅ Busca full-text
- ❌ Paginação (falha esperada — workspace tem apenas 2 documentos, precisa de ≥6)

### Classe `AssinafyE2ETest` (`test_e2e.py`)

```python
class AssinafyE2ETest:
    def __init__(self):
        self.session = requests.Session()  # Session com X-Api-Key
        self.results = []

    # 9 métodos de teste
    def test_authenticate(self)
    def test_list_accounts(self)
    def test_list_documents(self, account_id)
    def test_list_signers(self, account_id)
    def test_list_templates(self, account_id)
    def test_list_webhooks(self, account_id)
    def test_response_format(self, account_id)
    def test_pagination(self, account_id)
    def test_search(self, account_id)

    def run_all_tests(self)
```

### Padrão para Novos Testes

```python
def test_new_feature(self, account_id):
    """Test N: Descrição curta"""
    try:
        response = self.session.get(f"{BASE_URL}/accounts/{account_id}/endpoint", timeout=10)
        if response.status_code != 200:
            self.log("Nome", False, self._get_response_details(response))
            return False
        data = response.json()
        self.log("Nome", True, "Detalhes")
        return True
    except Exception as e:
        self.log("Nome", False, f"Erro: {e}")
        return False
```

Depois adicionar chamada em `run_all_tests()`.

---

## Documentação da API (`data/assinafy_api.json`)

**186KB, 84 endpoints documentados, 10 seções**

| Seção | Endpoints |
|-------|-----------|
| Signer | 38 |
| Document | 32 |
| Webhooks | 12 |
| Template | 2 |
| Authentication, Assignment, Field Definition | restantes |

Base URL: `https://api.assinafy.com.br/v1`

**Consultar via jq**:
```bash
cat data/assinafy_api.json | jq '.sections[] | {title: .title, endpoints: (.endpoints | length)}'
cat data/assinafy_api.json | jq '.sections[].endpoints[] | select(.path | contains("signers"))'
```

**Estrutura JSON**:
```json
{
  "base_url": "https://api.assinafy.com.br/v1",
  "extracted_at": "2026-03-24T21:48:09",
  "metadata": {"source": "html_scraping", "total_endpoints": 100},
  "sections": [
    {
      "title": "Signer",
      "level": 1,
      "endpoints": [
        {
          "title": "Creating Signers",
          "method": "GET",
          "path": "/accounts/{id}/signers",
          "parameters": [],
          "requires_auth": true
        }
      ]
    }
  ]
}
```

---

## Dependências (`pyproject.toml`)

**Runtime**:
- `requests>=2.31.0` — Cliente HTTP
- `python-dotenv>=1.0.0` — Carregar `.env`
- `click>=8.1.0` — Framework CLI
- `pyyaml>=6.0.0` — Configuração YAML
- `weasyprint>=66.0` — Geração de PDF (relatórios)

**Desenvolvimento**:
- `pytest>=7.4.0`, `pytest-cov>=4.1.0` — Testes
- `black>=23.0.0` — Formatação (line-length: 100, target: py39)
- `ruff>=0.1.0` — Linting (line-length: 100, target: py39)

**Entry point**: `assinafy = "assinafy.cli:cli"`

---

## Fluxo de Assinatura Digital

```
Upload PDF  →  Aguardar processamento  →  Enviar email com link
    ↓                    ↓                        ↓
upload_pdf()      wait_for_ready()        send_signing_email()
    ↓                    ↓                        ↓
document_id       polling a cada 2s       webbrowser.open(mailto:)
signing_url       timeout padrão: 60s
```

**Importante**: Todo documento criado via API já possui `signing_url` válido. Não é necessário adicionar signatários manualmente.

**Status do documento**:
- Processando: `uploaded`, `uploading`, `metadata_processing`, `certificating`
- Pronto: `metadata_ready`, `pending_signature`, `certificated`

---

## Problemas Conhecidos

- `adicionar_signatarios.py`: Endpoint de signatários retorna 404 (experimental)
- `assinafy/automation/signature.py`: Contém função `automate_signature` duplicada (linhas 17–86 e 88–156); a segunda versão referencia `wait_for_document_ready` inexistente — usar a primeira definição
- Teste de paginação sempre falha (workspace de desenvolvimento tem < 6 documentos)

---

## Documentação Adicional

- `docs/fluxo_documentos_assinafy.md` — Análise completa do processamento de documentos
- `docs/arquitetura.md` — Diagramas Mermaid, decisões de design e limitações
- `relatorio_testes_e2e.md` / `relatorio_testes_e2e.html` — Último relatório de execução E2E
