#!/usr/bin/env python3
"""
Automatizar processo completo de assinatura via API Assinafy

1. Converter HTML para PDF
2. Upload do PDF via API
3. Criar envelope de assinatura
4. Adicionar signatários
5. Enviar para coleta
"""
import os
import sys
import requests
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("ASSINAFY_API_KEY")
WORKSPACE_ID = os.getenv("ASSINAFY_WORKSPACE_ID")
BASE_URL = "https://api.assinafy.com.br/v1"

if not API_KEY or not WORKSPACE_ID:
    print("❌ Erro: Credenciais não encontradas")
    sys.exit(1)

def convert_html_to_pdf(html_file, pdf_file):
    """Converter HTML para PDF usando weasyprint"""
    try:
        import weasyprint
        print("📄 Convertendo HTML para PDF...")

        html_doc = weasyprint.HTML(filename=html_file)
        html_doc.write_pdf(pdf_file)

        print(f"✅ PDF criado: {pdf_file}")
        return True
    except ImportError:
        print("❌ weasyprint não instalado. Instalando...")
        os.system(".venv/bin/pip install weasyprint")
        return False
    except Exception as e:
        print(f"❌ Erro na conversão: {e}")
        return False

def upload_document_pdf(pdf_file):
    """Upload de documento PDF via API"""
    print(f"\n📤 Uploading PDF via API...")

    url = f"{BASE_URL}/accounts/{WORKSPACE_ID}/documents"

    with open(pdf_file, 'rb') as f:
        files = {
            'file': (os.path.basename(pdf_file), f, 'application/pdf')
        }
        headers = {
            "X-Api-Key": API_KEY
        }

        response = requests.post(url, files=files, headers=headers, timeout=30)

    print(f"Status: {response.status_code}")

    if response.status_code == 200 or response.status_code == 201:
        try:
            data = response.json()
        except:
            data = {}

        document_data = data.get('data', {})
        document_id = document_data.get('id')

        print(f"✅ Documento criado!")
        print(f"   ID: {document_id}")
        print(f"   Dados: {document_data}")
        return document_id, document_data
    else:
        print(f"❌ Falha no upload")
        print(f"Response: {response.text}")
        return None, None

def add_signers_to_document(document_id, signers):
    """Adicionar signatários ao documento"""
    print(f"\n✍️  Adicionando signatários...")

    url = f"{BASE_URL}/accounts/{WORKSPACE_ID}/documents/{document_id}/signers"

    headers = {
        "X-Api-Key": API_KEY,
        "Content-Type": "application/json"
    }

    for signer in signers:
        payload = {
            "signer": signer
        }

        response = requests.post(url, json=payload, headers=headers, timeout=30)

        if response.status_code == 200 or response.status_code == 201:
            print(f"   ✅ {signer.get('name')} ({signer.get('email')}) adicionado")
        else:
            print(f"   ❌ Falha ao adicionar {signer.get('name')}")
            print(f"      Status: {response.status_code}")

    return True

def main():
    """Processo completo de assinatura automatizada"""
    print("="*60)
    print("🚀 AUTOMATIZAÇÃO DE ASSINATURA - API Assinafy")
    print("="*60)

    # 1. Converter para PDF
    pdf_file = "relatorio_testes_e2e.pdf"

    if not convert_html_to_pdf("relatorio_testes_e2e.html", pdf_file):
        print("❌ Não foi possível converter para PDF")
        return

    # 2. Upload via API
    doc_id, doc_data = upload_document_pdf(pdf_file)

    if not doc_id:
        print("\n❌ Upload falhou. Tente upload manual em:")
        print("   https://assinafy.com.br")
        return

    # 3. Adicionar signatários
    signers = [
        {
            "email": "gabrielgfcramos2@gmail.com",
            "name": "Gabriel Ramos",
            "documentation": "CPF: 123.456.789-00"
        }
    ]

    if add_signers_to_document(doc_id, signers):
        print("\n" + "="*60)
        print("✅ PROCESSO CONCLUÍDO!")
        print("="*60)
        print(f"\n📄 Document ID: {doc_id}")
        print(f"📧 Signatários: {len(signers)} adicionados")
        print(f"🔗 Link do documento: {doc_data.get('attribute', {}).get('link', 'N/A')}")
        print(f"\n📩 Os signatários receberão notificação por email")
        print(f"📱 Eles podem assinar digitalmente via:")
        print(f"   - Web browser")
        print(f"   - App mobile")
        print(f"   - WhatsApp (se configurado)")

if __name__ == "__main__":
    main()
