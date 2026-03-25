#!/usr/bin/env python3
"""
Enviar email com link de assinatura do documento Assinafy
"""
import webbrowser
import urllib.parse

DOCUMENT_ID = "10235a92bf785028b2dbc45653ba"
SIGNING_URL = "https://app.assinafy.com.br/sign/10235a92bf785028b2dbc45653ba"
SIGNER_EMAIL = "gabrielgfcramos2@gmail.com"
DOCUMENT_NAME = "Termo de Adesão ASOF v2"

email_to = SIGNER_EMAIL
subject = f"📋 Documento para Assinatura Digital - {DOCUMENT_NAME}"

body = f"""Olá Gabriel,

Segue o link para assinar digitalmente o documento "{DOCUMENT_NAME}":

🔗 Link de Assinatura:
{SIGNING_URL}

📋 Informações:
- Documento: {DOCUMENT_NAME}
- Plataforma: Assinafy (https://assinafy.com.br)
- Document ID: {DOCUMENT_ID}

Como assinar:
1. Clique no link acima
2. Você será direcionado para a plataforma Assinafy
3. Faça login (se necessário)
4. Assine digitalmente usando as opções disponíveis:
   - Assinar na tela (touch/mouse)
   - Enviar por SMS
   - Usar certificado digital

Após assinar, o documento será automaticamente registrado.

Qualquer dúvida, entre em contato.

Atenciosamente,
Gabriel Ramos
"""

# Criar link mailto
subject_encoded = urllib.parse.quote(subject)
body_encoded = urllib.parse.quote(body.strip())

mailto_link = f"mailto:{email_to}?subject={subject_encoded}&body={body_encoded}"

print("📧 Abrindo cliente de email com rascunho...")
print()
print(f"📧 Rascunho aberto para: {email_to}")
print(f"📄 Documento: {DOCUMENT_NAME}")
print()
print("🔗 Link de Assinatura incluído no rascunho:")
print(f"   {SIGNING_URL}")
print()

# Abrir cliente de email
print("Abrindo cliente de email...")
webbrowser.open(mailto_link)

print("\n⚠️  Rascunho aberto no cliente de email.")
print(f"💡 Revise o conteúdo e clique em ENVIAR para {email_to}")
