# Fluxo de Processamento de Documentos - API Assinafy

**Data**: 2026-03-25
**Contexto**: Investigação do comportamento de upload e processamento de documentos via API Assinafy

## Status de Documentos

A API Assinafy possui os seguintes status para documentos (obtido via `GET /documents/statuses`):

| Status | Deletável | Descrição |
|--------|-----------|-----------|
| `uploading` | ❌ | Upload em progresso |
| `uploaded` | ❌ | Upload concluído |
| `metadata_processing` | ❌ | **Processando metadados** |
| `metadata_ready` | ✅ | Metadados processados, pronto para configuração |
| `pending_signature` | ✅ | Aguardando assinaturas |
| `certificating` | ❌ | Em certificação |
| `certificated` | ❌ | Certificado (assinatura concluída) |
| `expired` | ✅ | Expirado |
| `rejected_by_signer` | ✅ | Rejeitado por signatário |
| `rejected_by_user` | ✅ | Rejeitado pelo usuário |
| `failed` | ✅ | Falha no processamento |

## Fluxo Esperado

```
uploading → uploaded → metadata_processing → metadata_ready → pending_signature → certificating → certificated
```

## Problema Identificado

### Comportamento Observado

Após upload via API (`POST /accounts/{workspace_id}/documents`), os documentos ficam **travados no status `uploaded`** e não avançam para `metadata_processing`.

### Evidências

**Testes realizados em 2026-03-25**:

```
Document ID                              Status      Created At
10235ac07065e0293a93498cda0d           uploaded    2026-03-25T01:47:26Z
19d22ab389402af67b4fdcea0a5            uploaded    2026-03-25T01:45:39Z
10235a92bf785028b2dbc45653ba          uploaded    2026-03-25T01:42:26Z
19d22a69f75be139150ba677faa           failed      2026-03-25T01:40:38Z (test.txt)
10235a822d8a161015612934bb76          failed      2026-03-25T01:40:38Z (test.html)
```

- ✅ PDFs: Ficam em `uploaded` (não avançam)
- ❌ HTML/TXT: Vão direto para `failed` (formato não suportado)

### Tentativas de Solução

1. **Aguardar processamento (60 segundos)**
   - Script: `wait_for_document_ready()` em `automar_assinatura.py`
   - Resultado: Timeout em 60s, documento continua em `uploaded`

2. **Adicionar signatários via API**
   - Endpoint testado: `POST /accounts/{workspace_id}/documents/{doc_id}/signers`
   - Resultado: **404 Not Found**
   - Conclusão: Endpoint não existe ou foi descontinuado

## Descobertas sobre Endpoints

### Endpoints que Funcionam

| Método | Endpoint | Status |
|--------|----------|--------|
| POST | `/accounts/{workspace_id}/documents` | ✅ Upload de PDF |
| GET | `/documents/{id}` | ✅ Obter detalhes do documento |
| GET | `/documents/statuses` | ✅ Listar status possíveis |
| GET | `/accounts/{workspace_id}/documents` | ✅ Listar documentos do workspace |

### Endpoints que NÃO Funcionam

| Método | Endpoint | Problema |
|--------|----------|----------|
| POST | `/accounts/{workspace_id}/documents/{doc_id}/signers` | **404** - Endpoint não existe |

### Informação Importante

**Todo documento criado via API já possui um `signing_url`**:

```json
{
  "id": "10235ac07065e0293a93498cda0d",
  "status": "uploaded",
  "signing_url": "https://app.assinafy.com.br/sign/10235ac07065e0293a93498cda0d"
}
```

Isso significa que **não é necessário adicionar signatários via API** - o link já está pronto para uso.

## Formatos de Arquivo Suportados

| Formato | Suporte | Evidência |
|---------|---------|-----------|
| PDF | ✅ | Upload OK, status `uploaded` |
| HTML | ❌ | Upload OK, status `failed` |
| TXT | ❌ | Upload OK, status `failed` |

**Mensagem de erro para HTML**:
```json
{
  "status": 500,
  "message": "Unsupported file content: text/html"
}
```

## Análise e Recomendações

### Hipóteses para o Comportamento

1. **Processamento assíncrono muito lento**: Pode levar mais que 60 segundos (mas improvável)
2. **Configuração via interface web necessária**: Assinafy pode requerer configuração manual de signatários/campos antes do processamento
3. **Mudança na API**: Endpoints para configuração de signatários podem ter sido removidos
4. **Workspace/conta limitada**: Pode haver limitações no plano de teste

### Soluções Alternativas

#### Opção 1: Usar signing_url Diretamente (RECOMENDADO)

```python
# 1. Upload via API
response = requests.post(upload_url, files=files, headers=headers)
doc_id = response.json()['data']['id']
signing_url = response.json()['data']['signing_url']

# 2. Enviar email com signing_url
# O signatário acessa o link e a plataforma Assinafy lida com o processamento
```

**Vantagens**:
- ✅ Funciona imediatamente
- ✅ Não requer processamento prévio
- ✅ Plataforma Assinafy mostra status apropriado ao signatário

**Desvantagens**:
- ⚠️ Signatário pode ver mensagem "Processando" ao acessar o link
- ⚠️ Não é possível adicionar signatários via API

#### Opção 2: Configuração Manual Via Interface Web

1. Upload via API
2. Acessar https://app.assinafy.com.br
3. Configurar signatários manualmente
4. Isso pode disparar o processamento

#### Opção 3: Aguardar Mudanças na API

Monitorar documentação da Assinafy para:
- Novos endpoints para configuração de documentos
- Webhooks para notificações de mudança de status
- Documentação atualizada sobre o fluxo de processamento

## Implementação Atual

### Script: `automar_assinatura.py`

Fluxo implementado:

```python
def main():
    # 1. Upload do PDF
    document_id, signing_url = upload_pdf(pdf_path)

    # 2. Aguardar processamento (timeout 60s)
    if not wait_for_document_ready(document_id, timeout=60):
        print("⚠️ Documento não ficou pronto a tempo")
        print("💡 O email será enviado mesmo assim")

    # 3. Enviar email com signing_url
    send_signing_email(signing_url, document_name, signer_email, signer_name)
```

**Resultado**: Email enviado mesmo com documento em `uploaded`

### Scripts Auxiliares

| Script | Propósito |
|--------|-----------|
| `test_upload_pdf.py` | Teste isolado de upload |
| `enviar_link_assinatura.py` | Enviar email com link existente |
| `adicionar_signatarios.py` | **NÃO FUNCIONA** - endpoint 404 |
| `explore_signers.py` | Explorar estrutura de signatários |

## Conclusão

### O Que Funciona

✅ Upload de PDFs via API
✅ Obtenção de `signing_url` imediato
✅ Envio de email com link de assinatura
✅ Consulta de status de documentos

### O Que NÃO Funciona

❌ Processamento automático de metadados (trava em `uploaded`)
❌ Adição de signatários via API (endpoint 404)
❌ Upload de HTML/TXT (formato não suportado)

### Recomendação Final

**Usar Opção 1**: Enviar `signing_url` imediatamente após upload, sem aguardar processamento. A plataforma Assinafy lidará com o processamento quando o signatário acessar o link.

```python
# Fluxo recomendado
upload_pdf() → get_signing_url() → send_email()
# Não aguardar processamento
```

### Próximos Passos

1. **Monitorar**: Verificar se documentos eventualmente mudam de status (após algumas horas)
2. **Contatar suporte Assinafy**: Perguntar sobre:
   - Tempo esperado de processamento
   - Endpoints corretos para configuração de signatários
   - Webhooks disponíveis
3. **Testar com signatário real**: Verificar experiência do usuário ao acessar `signing_url` com documento em `uploaded`

## Referências

- **Base URL**: https://api.assinafy.com.br/v1
- **Documentação**: https://api.assinafy.com.br/v1/docs
- **Plataforma**: https://app.assinafy.com.br
- **Workspace ID**: [configurado em .env]
