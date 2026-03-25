# Plano: Corrigir Issues Pendentes do CodeRabbit

## Contexto

Após as correções iniciais, restam 4 categorias de issues do CodeRabbit pendentes:

1. **data/assinafy_api.json** - Arquivo gerado automaticamente com problemas estruturais
2. **test_upload_pdf.py** - PDF_FILE hardcoded (script legado)
3. **automatizar_assinatura.py** - Logging de PII (emails em logs INFO)
4. **ARCHITECTURE.md** - Sugestões de documentação

## Análise dos Problemas

### 1. data/assinafy_api.json (Arquivo Gerado)

**Problemas identificados:**
- **Entradas duplicadas**: "Creating Signers" aparece 2x, "List" 2x, etc.
- **IDs hardcoded**: Paths com IDs reais como "615601fab04c0a31", "35c7741ca4006b9e11"
- **Métodos incorretos**: Endpoints de criação marcados como GET em vez de POST
- **requires_auth: false**: Muitos endpoints marcados como não requerem autenticação

**Impacto:** Baixo - arquivo é gerado automaticamente por scraper, documentação apenas

**Decisão:** **NÃO corrigir agora** - Issue cosmético em arquivo gerado
- Scraper pode ser melhorado no futuro (fase separada)
- Correção manual seria perdida na próxima geração
- Prioridade: Baixa

### 2. test_upload_pdf.py (Script Legado)

**Problema:** PDF_FILE hardcoded com path específico do usuário
```python
# Exemplo de path hardcoded (antes da correção):
# PDF_FILE = "/Users/gabrielramos/Downloads/ASOF_Termo_de_Adesao_v2 (1).pdf"
```

**Solução proposta:** Aceitar argumento de linha de comando
```python
# Linha 25: Substituir
PDF_FILE = sys.argv[1] if len(sys.argv) > 1 else "/path/to/default.pdf"
```

**Impacto:** Baixo - script legado com uso limitado
**Decisão:** **Corrigir** - Melhora usabilidade sem muito esforço

### 3. automatizar_assinatura.py (PII em Logs)

**Problemas:** Emails expostos em logs INFO nível
```python
# Linhas 151, 217, 248
logger.info(f"Signatário: {signer_name} ({signer_email})")
```

**Solução proposta:** Mascarar emails em INFO, manter completo em DEBUG
```python
def mask_email(email: str) -> str:
    """Mascara email: user@domain.com → u***@domain.com"""
    if '@' not in email:
        return email
    username, domain = email.split('@', 1)
    return f"{username[0]}***@{domain}"

# Usar:
logger.info(f"Signatário: {signer_name} ({mask_email(signer_email)})")
```

**Impacto:** Médio - Segurança de dados em logs
**Decisão:** **Corrigir** - Boa prática para segurança

### 4. ARCHITECTURE.md (Documentação)

**Problemas:** 3 sugestões de atualização
- Adicionar cross-references entre roadmap e known limitations
- Expandir seção de testes prioritários
- Atualizar versão do Python

**Impacto:** Baixo - Documentação apenas
**Decisão:** **POSTERGAR** - Documentação pode ser atualizada depois

## Plano de Implementação

### Fase 1: Corrigir PII em Logs (Média Prioridade)

**Arquivo:** `automatizar_assinatura.py`

**Mudanças:**
1. Adicionar função `mask_email()` no topo do arquivo (após imports)
2. Substituir 3 ocorrências de `logger.info(f"... ({signer_email})")` por `mask_email(signer_email)`
3. Manter logs DEBUG inalterados (dados completos para troubleshooting)

**Linhas:** 151, 217, 248

### Fase 2: Corrigir PDF_FILE Hardcoded (Baixa Prioridade)

**Arquivo:** `test_upload_pdf.py`

**Mudança:**
1. Substituir linha 25: `PDF_FILE = sys.argv[1] if len(sys.argv) > 1 else "/path/to/default.pdf"`
2. Adicionar verificação de existência e mensagem de uso

**Notas:**
- Script legado com uso limitado
- Manter compatibilidade com uso existente
- Fornecer mensagem de erro clara

### Fase 3: Testes e Validação

**Testes:**
1. Executar `pytest tests/ -v` (21/21 passing)
2. Testar `automatizar_assinatura.py` manualmente
3. Verificar logs não exibem emails completos em INFO

### Arquivos a Modificar

**Fase 1:**
- `automatizar_assinatura.py` (+ função mask_email, 3 substituições)

**Fase 2:**
- `test_upload_pdf.py` (1 linha)

### Arquivos NÃO Modificados

- `data/assinafy_api.json` - Arquivo gerado, melhorias em scraper separado
- `ARCHITECTURE.md` - Documentação pode esperar

## Verificação

1. **Testes unitários:** `pytest tests/ -v` → 21/21 passing
2. **Teste PII:** Executar script e verificar logs não mostram emails completos
3. **Teste PDF_FILE:** Testar com argumento de linha de comando

## Riscos e Mitigações

**Risco:** Quebrar funcionalidade existente
**Mitigação:** Testes completos antes de commit

**Risco:** Logs menos úteis para debugging
**Mitigação:** Nível DEBUG ainda mostra dados completos

**Risco:** Compatibilidade com scripts que esperam comportamento antigo
**Mitigação:** Scripts legados mantêm interface consistente
