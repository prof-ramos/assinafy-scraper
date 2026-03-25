# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Purpose

Este repositório contém a **documentação extraída da API Assinafy** em formato JSON estruturado. A documentação foi raspada de https://api.assinafy.com.br/v1/docs em 2026-03-24.

## Documentação

**Arquivo**: `data/assinafy_api.json` (186KB)

**Conteúdo**:
- 84 endpoints documentados
- 10 seções organizadas (Signer, Document, Template, Webhooks, etc.)
- Métodos HTTP, paths, parâmetros e exemplos
- Base URL: https://api.assinafy.com.br/v1

## Como Usar

### Via jq
```bash
# Ver todas as seções
cat data/assinafy_api.json | jq '.sections[] | {title: .title, endpoints: (.endpoints | length)}'

# Buscar endpoint específico
cat data/assinafy_api.json | jq '.sections[].endpoints[] | select(.path | contains("signers"))'

# Ver parâmetros de um endpoint
cat data/assinafy_api.json | jq '.sections[3].endpoints[0].parameters'
```

### Via Python
```python
import json

with open('data/assinafy_api.json') as f:
    docs = json.load(f)

# Acessar endpoints
for section in docs['sections']:
    for endpoint in section['endpoints']:
        print(f"{endpoint['method']} {endpoint['path']}")
```

## Estrutura do JSON

```json
{
  "base_url": "https://api.assinafy.com.br/v1",
  "extracted_at": "2026-03-24T21:48:09.425269",
  "metadata": {
    "source": "html_scraping",
    "pages_scraped": 1,
    "total_endpoints": 100
  },
  "sections": [
    {
      "title": "Signer",
      "level": 1,
      "endpoints": [
        {
          "title": "Creating Signers",
          "method": "GET",
          "path": "/accounts/{id}/signers",
          "description": "...",
          "parameters": [],
          "request_example": null,
          "response_example": null,
          "requires_auth": false,
          "supports_pagination": false
        }
      ]
    }
  ]
}
```

## Autenticação

Credenciais da API Assinafy estão no arquivo `.env`:
- `USUARIO`: gabriel@asof.org.br
- `ASSINAFY_API_KEY`: API key para autenticação
- `ASSINAFY_WORKSPACE_ID`: ID do workspace

**Headers de autenticação**:
```
X-Api-Key: <ASSINAFY_API_KEY>
Authorization: Bearer <access_token>
```

## Seções Principais

- **Signer** (38 endpoints): Gestão de signatários
- **Document** (32 endpoints): Gestão de documentos
- **Template** (2 endpoints): Templates de documento
- **Webhooks** (12 endpoints): Webhooks e eventos

## Paths Normalizados

IDs de exemplo foram substituídos por placeholders:
- MongoDB IDs: `/abc123...` → `/{id}`
- UUIDs: `/123e4567-...` → `/{uuid}`
- Numéricos: `/1234` → `/{id}`
