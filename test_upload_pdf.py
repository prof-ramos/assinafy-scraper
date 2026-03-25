#!/usr/bin/env python3
"""
Testar upload de PDF específico via API Assinafy
"""
import os
import sys
import requests
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("ASSINAFY_API_KEY")
WORKSPACE_ID = os.getenv("ASSINAFY_WORKSPACE_ID")
BASE_URL = "https://api.assinafy.com.br/v1"

PDF_FILE = "/Users/gabrielramos/Downloads/ASOF_Termo_de_Adesao_v2 (1).pdf"

if not API_KEY or not WORKSPACE_ID:
    print("❌ Erro: Credenciais não encontradas")
    sys.exit(1)

if not os.path.exists(PDF_FILE):
    print(f"❌ Arquivo não encontrado: {PDF_FILE}")
    sys.exit(1)

def upload_pdf():
    """Fazer upload do PDF via API Assinafy"""
    print("="*60)
    print("📤 Upload de PDF via API Assinafy")
    print("="*60)
    print(f"\n📄 Arquivo: {PDF_FILE}")
    print(f"📏 Tamanho: {os.path.getsize(PDF_FILE) / 1024:.1f} KB")
    print(f"🆔 Workspace: {WORKSPACE_ID}")
    print()

    url = f"{BASE_URL}/accounts/{WORKSPACE_ID}/documents"

    with open(PDF_FILE, 'rb') as f:
        files = {
            'file': (os.path.basename(PDF_FILE), f, 'application/pdf')
        }
        headers = {
            "X-Api-Key": API_KEY
        }

        print("📡 Enviando requisição...")
        response = requests.post(url, files=files, headers=headers, timeout=30)

    print(f"\n📊 Status HTTP: {response.status_code}")

    if response.status_code == 200 or response.status_code == 201:
        try:
            data = response.json()
        except:
            data = {}

        document_data = data.get('data', {})
        document_id = document_data.get('id')
        title = document_data.get('title', 'Sem título')
        status = document_data.get('status', 'unknown')

        print(f"✅ Upload realizado com sucesso!")
        print(f"\n📄 Document ID: {document_id}")
        print(f"📋 Título: {title}")
        print(f"📌 Status: {status}")

        # Mostrar todos os dados recebidos
        print(f"\n📦 Dados completos:")
        print(f"   {document_data}")

        return document_id, document_data

    else:
        print(f"❌ Falha no upload")
        print(f"\n📝 Response:")
        print(f"   {response.text}")

        return None, None

def list_all_documents():
    """Listar todos os documentos do workspace"""
    print("\n" + "="*60)
    print("📋 Documentos no Workspace")
    print("="*60)
    print()

    url = f"{BASE_URL}/accounts/{WORKSPACE_ID}/documents"
    headers = {
        "X-Api-Key": API_KEY
    }

    response = requests.get(url, headers=headers, timeout=30)

    if response.status_code == 200:
        data = response.json()
        docs = data.get('data', [])

        print(f"📊 Total de documentos: {len(docs)}\n")

        for i, doc in enumerate(docs, 1):
            doc_id = doc.get('id')
            title = doc.get('title', 'Sem título')
            status = doc.get('status', 'unknown')
            created = doc.get('created_at', 'N/A')

            print(f"{i}. {title}")
            print(f"   ID: {doc_id}")
            print(f"   Status: {status}")
            print(f"   Criado: {created}")
            print()
    else:
        print(f"❌ Falha ao listar: {response.text}")

if __name__ == "__main__":
    # Listar documentos antes
    list_all_documents()

    # Tentar upload
    doc_id, doc_data = upload_pdf()

    if doc_id:
        print("\n" + "="*60)
        print("🎉 SUCESSO!")
        print("="*60)
        print(f"\n📄 Documento foi adicionado ao workspace!")
        print(f"🔗 Para acessar: https://assinafy.com.br")
        print(f"\n💡 Próximos passos:")
        print(f"   1. Acesse o documento na plataforma")
        print(f"   2. Adicione signatários")
        print(f"   3. Envie para coleta de assinaturas")
