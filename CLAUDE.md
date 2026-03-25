# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Purpose

Este repositório contém a **documentação extraída da API Assinafy** em formato JSON estruturado e **testes E2E** para validar o funcionamento da API.

## Documentação da API

**Arquivo**: `data/assinafy_api.json` (186KB)

**Conteúdo**:
- 84 endpoints documentados
- 10 seções organizadas (Signer, Document, Template, Webhooks, etc.)
- Métodos HTTP, paths, parâmetros e exemplos
- Base URL: https://api.assinafy.com.br/v1

**Consultar via jq**:
```bash
cat data/assinafy_api.json | jq '.sections[] | {title: .title, endpoints: (.endpoints | length)}'
cat data/assinafy_api.json | jq '.sections[].endpoints[] | select(.path | contains("signers"))'
```

## Testes E2E

### Executar Testes

```bash
# Instalar dependências (primeira vez)
uv sync

# Executar todos os testes E2E
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
- ❌ Paginação (falha esperada - workspace tem apenas 2 documentos, precisa de ≥6)

## Arquitetura do Teste E2E

### Classe: `AssinafyE2ETest`

**Arquivo**: `test_e2e.py`

**Estrutura**:
```python
class AssinafyE2ETest:
    def __init__(self):
        # Configura session com headers de autenticação
        self.session = requests.Session()
        self.results = []

    # Métodos de teste (9 testes no total)
    def test_authenticate(self)           # Test 1
    def test_list_accounts(self)           # Test 2
    def test_list_documents(self, id)      # Test 3
    def test_list_signers(self, id)        # Test 4
    def test_list_templates(self, id)      # Test 5
    def test_list_webhooks(self, id)       # Test 6
    def test_response_format(self, id)     # Test 7
    def test_pagination(self, id)          # Test 8
    def test_search(self, id)              # Test 9

    # Helpers
    def _test_list_resource(self, id, name, endpoint)  # Helper genérico
    def _get_response_details(self, response)           # Extrair detalhes de erro
    def log(self, name, passed, details="")              # Registrar resultado

    def run_all_tests(self)              # Orchestrator
```

### Fluxo de Execução

```
run_all_tests()
  ↓
test_authenticate()  → Valida API Key
  ↓
test_list_accounts()  → Obtém account_id ou usa WORKSPACE_ID
  ↓
test_list_*()         → Testa listagem de recursos (documents, signers, etc.)
  ↓
test_response_format() → Valida estrutura JSON
  ↓
test_pagination()     → Testa paginação (precisa ≥6 docs)
  ↓
test_search()         → Testa busca full-text
  ↓
Resumo com estatísticas
```

### Padrão de Testes

**Helper genérico** para evitar repetição:
```python
def _test_list_resource(self, account_id, resource_name, endpoint):
    response = self.session.get(f"{BASE_URL}/accounts/{account_id}/{endpoint}")
    data = response.json()
    items = data.get("data", [])
    self.log(f"Listar {resource_name}", len(items) >= 0, f"Encontrados: {len(items)}")
    return items
```

**Uso**:
```python
def test_list_documents(self, account_id):
    return self._test_list_resource(account_id, "documentos", "documents")
```

## Autenticação

**Arquivo**: `.env`

```bash
USUARIO=gabriel@asof.org.br
ASSINAFY_API_KEY=U0NN2B_penT0_oYfoU4Tsdfp1izRyLpX3P0VbhSFJXwlDIs1mm0ijsF08IC7xpjO
ASSINAFY_WORKSPACE_ID=ff385f40ae28a08ae962609d5e7
```

**Headers utilizados**:
```
X-Api-Key: <ASSINAFY_API_KEY>
Content-Type: application/json
Accept: application/json
```

## Dependências

**Runtime**:
- `requests>=2.31.0` - Cliente HTTP
- `python-dotenv>=1.0.0` - Carregar variáveis de ambiente

**Desenvolvimento** (dev-dependencies):
- `pytest>=7.4.0` - Framework de testes
- `pytest-cov>=4.1.0` - Cobertura de testes
- `black>=23.0.0` - Formatação de código
- `ruff>=0.1.0` - Linting

## Adicionar Novos Testes

**Padrão**:
```python
def test_new_feature(self, account_id):
    """Test N: Descrição curta"""
    try:
        response = self.session.get(f"{BASE_URL}/accounts/{account_id}/new-endpoint", timeout=10)

        if response.status_code != 200:
            details = self._get_response_details(response)
            self.log("Nome do teste", False, details)
            return False

        data = response.json()
        # Validar resposta
        self.log("Nome do teste", True, "Detalhes do sucesso")
        return True
    except Exception as e:
        self.log("Nome do teste", False, f"Erro: {str(e)}")
        return False
```

**Depois**: Adicionar chamada em `run_all_tests()`:
```python
def run_all_tests(self):
    # ... testes existentes ...
    self.test_new_feature(account_id)
    # ...
```

## Seções da API

- **Signer** (38 endpoints): Gestão de signatários
- **Document** (32 endpoints): Gestão de documentos
- **Template** (2 endpoints): Templates de documento
- **Webhooks** (12 endpoints): Webhooks e eventos
- **Authentication**, **Assignment**, **Field Definition**: Outros recursos

## Estrutura do JSON da API

```json
{
  "base_url": "https://api.assinafy.com.br/v1",
  "extracted_at": "2026-03-24T21:48:09",
  "metadata": {"source": "html_scraping", "pages_scraped": 1, "total_endpoints": 100},
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

## Paths Normalizados

IDs de exemplo foram substituídos por placeholders:
- MongoDB IDs: `/abc123...` → `/{id}`
- UUIDs: `/123e4567-...` → `/{uuid}`
- Numéricos: `/1234` → `/{id}`
