# Guia de Migração para CLI Assinafy

Este guia ajuda você a migrar dos scripts legados para a nova CLI `assinafy`.

## Visão Geral

A nova CLI `assinafy` oferece:
- ✅ Interface unificada para todas as operações
- ✅ Argumentos via linha de comando (sem hardcoded values)
- ✅ Sistema de configuração (YAML + environment variables)
- ✅ Logging estruturado com níveis de verbosidade
- ✅ Melhor separação de responsabilidades

## Scripts Legados vs CLI

### Automatizar Assinatura Digital

**Script legado** (`automatizar_assinatura.py`):
```bash
# Precisa editar o arquivo para mudar parâmetros
.venv/bin/python automatizar_assinatura.py
```

**Nova CLI**:
```bash
# Parâmetros via linha de comando
.venv/bin/python assinafy_cli.py automate documento.pdf \
  --email user@example.com \
  --name "User Name"

# Ou usar o comando instalado
assinafy automate documento.pdf -e user@example.com -n "User Name"
```

### Upload de PDF

**Script legado** (`test_upload_pdf.py`):
```bash
# Precisa editar PDF_FILE no código
.venv/bin/python test_upload_pdf.py
```

**Nova CLI**:
```bash
# Especificar arquivo como argumento
.venv/bin/python assinafy_cli.py upload documento.pdf

# Ou
assinafy upload documento.pdf
```

### Enviar Link de Assinatura

**Script legado** (`enviar_link_assinatura.py`):
```bash
# Precisa editar DOCUMENT_ID, SIGNER_EMAIL no código
.venv/bin/python enviar_link_assinatura.py
```

**Nova CLI**:
```bash
# Especificar ID e email como argumentos
.venv/bin/python assinafy_cli.py send-link DOCUMENT_ID \
  --email user@example.com \
  --name "User Name"

# Ou
assinafy send-link DOCUMENT_ID -e user@example.com -n "User Name"
```

## Instalação da CLI

### Método 1: Usar diretamente com Python

```bash
.venv/bin/python assinafy_cli.py --help
```

### Método 2: Instalar como comando do sistema

```bash
# Sincronizar dependências
uv sync

# Instalar o pacote em modo editável
uv pip install -e .

# Agora você pode usar o comando diretamente
assinafy --help
```

## Verbosidade e Logging

A nova CLI suporta 3 níveis de verbosidade:

```bash
# ERROR (apenas erros) - padrão
assinafy upload documento.pdf

# INFO (progresso)
assinafy -v upload documento.pdf

# DEBUG (detalhes técnicos)
assinafy -vv upload documento.pdf
```

## Configuração

### Arquivo .env (Credenciais)

Manteve-se igual ao antes:

```bash
ASSINAFY_API_KEY=sua_chave_aqui
ASSINAFY_WORKSPACE_ID=seu_workspace_aqui
```

### Arquivo YAML (Configurações Opcionais)

Novo recurso - você pode criar um arquivo YAML para configurações não-sensíveis:

```bash
cp config/default.yaml.example config/custom.yaml
# Edite custom.yaml conforme necessário
```

Uso:
```bash
assinafy -c config/custom.yaml upload documento.pdf
```

## Comparação de Funcionalidades

| Funcionalidade | Script Legado | Nova CLI |
|----------------|---------------|----------|
| Upload de PDF | `test_upload_pdf.py` | `assinafy upload` |
| Automatizar fluxo completo | `automatizar_assinatura.py` | `assinafy automate` |
| Enviar link existente | `enviar_link_assinatura.py` | `assinafy send-link` |
| Verbosidade | Não disponível | `-v`, `-vv` |
| Config customizada | Não disponível | `-c config.yaml` |
| Parâmetros via CLI | Não (hardcoded) | ✅ Sim |
| Logging estruturado | ✅ Sim | ✅ Sim |

## Exemplos de Migração

### Exemplo 1: Upload Simples

**Antes**:
```bash
# Editar test_upload_pdf.py, mudar PDF_FILE
.venv/bin/python test_upload_pdf.py
```

**Depois**:
```bash
assinafy upload ~/Downloads/contrato.pdf
```

### Exemplo 2: Fluxo Completo

**Antes**:
```bash
# Editar automatizar_assinatura.py:
# - PDF_FILE = "~/Downloads/contrato.pdf"
# - SIGNER_EMAIL = "cliente@email.com"
# - SIGNER_NAME = "João Silva"
# - DOCUMENT_NAME = "Contrato de Serviços"

.venv/bin/python automatizar_assinatura.py
```

**Depois**:
```bash
assinafy automate ~/Downloads/contrato.pdf \
  --email cliente@email.com \
  --name "João Silva" \
  --document-name "Contrato de Serviços"
```

### Exemplo 3: Enviar Link para Documento Existente

**Antes**:
```bash
# Editar enviar_link_assinatura.py:
# - DOCUMENT_ID = "abc123"
# - SIGNER_EMAIL = "cliente@email.com"

.venv/bin/python enviar_link_assinatura.py
```

**Depois**:
```bash
assinafy send-link abc123 --email cliente@email.com
```

## Scripts Legados Ainda Disponíveis

Todos os scripts legados continuam funcionando e receberam logging estruturado:

- ✅ `automatizar_assinatura.py`
- ✅ `test_upload_pdf.py`
- ✅ `enviar_link_assinatura.py`

Eles são mantidos por compatibilidade, mas **recomendamos usar a nova CLI** para novos projetos.

## Suporte e Problemas

### CLI não encontrada

Se `assinafy` command não funcionar:

```bash
# Reinstalar o pacote
uv pip install -e .

# Ou usar o wrapper direto
.venv/bin/python assinafy_cli.py
```

### Erro de configuração

Certifique-se de que o arquivo `.env` existe:

```bash
cp .env.example .env
# Edite .env com suas credenciais
```

### Verificar instalação

```bash
# Verificar versão
assinafy --help

# Verificar se as dependências estão instaladas
uv sync
```

## Próximos Passos

1. **Experimente a CLI**: Comece com `assinafy upload` para testar
2. **Configure verbosidade**: Use `-v` ou `-vv` conforme necessário
3. **Crie config YAML**: Opcional, mas útil para configurações customizadas
4. **Migre gradualmente**: Você pode usar scripts legados e CLI em paralelo

## Referências

- **README.md**: Documentação geral do projeto
- **docs/arquitetura.md**: Arquitetura do sistema
- **assinafy --help**: Ajuda inline da CLI
