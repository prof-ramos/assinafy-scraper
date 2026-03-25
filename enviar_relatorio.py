#!/usr/bin/env python3
"""
Enviar relatório de testes por email usando mailto link
"""
import urllib.parse
import webbrowser

email_destino = "gabrielgfcramos2@gmail.com"
assunto = "Relatório de Testes E2E - API Assinafy para Assinatura"
corpo = """
Olá,

Segue em anexo o relatório de testes E2E da API Assinafy para assinatura digital.

RESUMO EXECUTIVO:
- 9 testes executados
- 8 testes aprovados (88% de sucesso)
- Status: API OPERACIONAL
- Data: 24/ Março/ 2026

O relatório completo está anexado a este e-mail.

Por favor, assine digitalmente usando a plataforma Assinafy.

Atenciosamente,
Equipe de Testes
"""

# Criar link mailto
assunto_encoded = urllib.parse.quote(assunto)
corpo_encoded = urllib.parse.quote(corpo.strip())

mailto_link = f"mailto:{email_destino}?subject={assunto_encoded}&body={corpo_encoded}"

print("📧 Link para enviar email:")
print(mailto_link)
print()
print("Ou use o comando abaixo para abrir no cliente de email padrão:")
webbrowser.open(mailto_link)
