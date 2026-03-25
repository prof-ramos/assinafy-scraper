#!/usr/bin/env python3
"""
Automatizar o fluxo completo de assinatura digital via API Assinafy

Fluxo:
1. Upload do PDF
2. Obter signing_url
3. Enviar email com link de assinatura
"""
import os
import sys
import time
import json
import webbrowser
import urllib.parse
import requests
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("ASSINAFY_API_KEY")
WORKSPACE_ID = os.getenv("ASSINAFY_WORKSPACE_ID")
BASE_URL = "https://api.assinafy.com.br/v1"


def wait_for_document_ready(document_id: str, timeout: int = 60) -> bool:
    """Aguardar o documento ficar pronto (metadata_ready ou pending_signature)"""
    url = f"{BASE_URL}/documents/{document_id}"
    headers = {"X-Api-Key": API_KEY}

    ready_statuses = {"metadata_ready", "pending_signature", "certificated"}
    processing_statuses = {"uploaded", "uploading", "metadata_processing", "certificating"}

    start_time = time.time()
    last_status = None

    print("\n⏳ Aguardando processamento do documento...")

    while time.time() - start_time < timeout:
        try:
            response = requests.get(url, headers=headers, timeout=10)

            if response.status_code != 200:
                time.sleep(2)
                continue

            data = response.json()
            document_data = data.get('data', {})
            status = document_data.get('status')

            if status != last_status:
                print(f"   📊 Status atual: {status}")
                last_status = status

            if status in ready_statuses:
                print(f"   ✅ Documento pronto para assinatura!")
                return True

            if status in processing_statuses:
                time.sleep(2)
                continue

            # Status não esperado
            print(f"   ⚠️  Status inesperado: {status}")
            return False

        except Exception as e:
            print(f"   ❌ Erro ao verificar status: {e}")
            time.sleep(2)
            continue

    print(f"   ⏱️  Timeout: documento não ficou pronto em {timeout}s")
    return False


def upload_pdf(pdf_path: str) -> tuple[str, str] | tuple[None, None]:
    """Fazer upload do PDF e retornar (document_id, signing_url)"""
    if not os.path.exists(pdf_path):
        print(f"❌ Arquivo não encontrado: {pdf_path}")
        return None, None

    print("="*60)
    print("📤 Upload de PDF via API Assinafy")
    print("="*60)
    print(f"\n📄 Arquivo: {pdf_path}")
    print(f"📏 Tamanho: {os.path.getsize(pdf_path) / 1024:.1f} KB")
    print()

    url = f"{BASE_URL}/accounts/{WORKSPACE_ID}/documents"

    with open(pdf_path, 'rb') as f:
        files = {
            'file': (os.path.basename(pdf_path), f, 'application/pdf')
        }
        headers = {
            "X-Api-Key": API_KEY
        }

        print("📡 Enviando requisição...")
        response = requests.post(url, files=files, headers=headers, timeout=30)

    print(f"\n📊 Status HTTP: {response.status_code}")

    if response.ok:
        try:
            data = response.json()
        except (json.JSONDecodeError, ValueError) as e:
            print(f"⚠️  Erro ao decodificar JSON: {e}")
            data = {}

        document_data = data.get('data', {})
        document_id = document_data.get('id')
        signing_url = document_data.get('signing_url')
        title = document_data.get('title', os.path.basename(pdf_path))
        status = document_data.get('status')

        print(f"✅ Upload realizado com sucesso!")
        print(f"\n📄 Document ID: {document_id}")
        print(f"📋 Título: {title}")
        print(f"📌 Status: {status}")
        print(f"🔗 Signing URL: {signing_url}")

        return document_id, signing_url
    else:
        print(f"❌ Falha no upload")
        print(f"\n📝 Response:")
        print(f"   {response.text}")
        return None, None


def send_signing_email(
    signing_url: str,
    document_name: str,
    signer_email: str,
    signer_name: str
) -> None:
    """Enviar email com link de assinatura"""
    print("\n" + "="*60)
    print("📧 Abrindo cliente de email com rascunho")
    print("="*60)
    print(f"\n👤 Signatário: {signer_name}")
    print(f"📧 Email: {signer_email}")
    print()

    subject = f"📋 Documento para Assinatura Digital - {document_name}"

    body = f"""Olá {signer_name},

Segue o link para assinar digitalmente o documento "{document_name}":

🔗 Link de Assinatura:
{signing_url}

📋 Informações:
- Documento: {document_name}
- Plataforma: Assinafy (https://assinafy.com.br)

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
Equipe ASOF
"""

    # Criar link mailto
    subject_encoded = urllib.parse.quote(subject)
    body_encoded = urllib.parse.quote(body.strip())

    mailto_link = f"mailto:{signer_email}?subject={subject_encoded}&body={body_encoded}"

    print(f"✅ Rascunho preparado para: {signer_email}")
    print(f"\n🔗 Link de Assinatura incluído no rascunho:")
    print(f"   {signing_url}")
    print()

    # Abrir cliente de email
    print("Abrindo cliente de email...")
    webbrowser.open(mailto_link)

    print("\n⚠️  Rascunho aberto no cliente de email.")
    print(f"💡 Revise o conteúdo e clique em ENVIAR para {signer_email}")


def main(
    pdf_path: str,
    signer_email: str,
    signer_name: str,
    document_name: str | None = None
) -> None:
    """Fluxo completo de automação de assinatura"""
    # Validar credenciais
    if not API_KEY or not WORKSPACE_ID:
        print("❌ Erro: Credenciais não encontradas no arquivo .env")
        sys.exit(1)

    # Usar nome do arquivo como document_name se não fornecido
    if not document_name:
        document_name = os.path.basename(pdf_path)

    # Passo 1: Upload do PDF
    document_id, signing_url = upload_pdf(pdf_path)

    if not document_id or not signing_url:
        print("\n❌ Falha no upload. Verifique os erros acima.")
        sys.exit(1)

    # Passo 1.5: Aguardar processamento do documento
    if not wait_for_document_ready(document_id, timeout=60):
        print("\n⚠️  Documento não ficou pronto a tempo.")
        print("💡 O email será enviado mesmo assim, mas o signatário pode ter dificuldades.")
        print("💡 Recomendação: Verifique o status do documento na plataforma Assinafy.")

    # Passo 2: Enviar email com link de assinatura
    send_signing_email(
        signing_url=signing_url,
        document_name=document_name,
        signer_email=signer_email,
        signer_name=signer_name
    )

    print("\n" + "="*60)
    print("🎉 FLUXO COMPLETO CONCLUÍDO!")
    print("="*60)
    print(f"\n✅ Documento enviado com sucesso!")
    print(f"📄 Document ID: {document_id}")
    print(f"👤 Signatário: {signer_name} ({signer_email})")
    print(f"\n💡 Próximos passos:")
    print(f"   1. O signatário receberá um email")
    print(f"   2. Ele pode assinar usando o link no email")
    print(f"   3. Ou acessar: https://app.assinafy.com.br")
    print(f"   4. Buscar pelo documento e assinar")


if __name__ == "__main__":
    # Configurações
    PDF_FILE = "/Users/gabrielramos/Downloads/ASOF_Termo_de_Adesao_v2 (1).pdf"
    SIGNER_EMAIL = "gabrielgfcramos2@gmail.com"
    SIGNER_NAME = "Gabriel Ramos"
    DOCUMENT_NAME = "Termo de Adesão ASOF v2"

    main(
        pdf_path=PDF_FILE,
        signer_email=SIGNER_EMAIL,
        signer_name=SIGNER_NAME,
        document_name=DOCUMENT_NAME
    )
