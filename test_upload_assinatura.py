#!/usr/bin/env python3
"""
Teste de Upload de Documento via API Assinafy

Automatizar o processo de:
1. Upload do documento HTML
2. Criação de envelope para assinatura
3. Adição de signatários
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

def upload_document(file_path):
    """Test 1: Upload de documento"""
    print("📤 Testando upload de documento...")

    url = f"{BASE_URL}/accounts/{WORKSPACE_ID}/documents"

    # Ler arquivo HTML
    with open(file_path, 'rb') as f:
        files = {
            'file': ('relatorio_testes_e2e.html', f, 'text/html')
        }
        headers = {
            "X-Api-Key": API_KEY
        }

        response = requests.post(url, files=files, headers=headers, timeout=30)

    print(f"Status: {response.status_code}")
    print(f"Response: {response.text[:500]}")

    if response.status_code == 200 or response.status_code == 201:
        data = response.json()
        document_id = data.get('data', {}).get('id')
        print(f"✅ Documento criado! ID: {document_id}")
        return document_id
    else:
        print("❌ Falha no upload")
        return None

def create_sign_envelope(document_id, signers):
    """Test 2: Criar envelope para assinatura"""
    print("\n📋 Testando criação de envelope de assinatura...")

    url = f"{BASE_URL}/accounts/{WORKSPACE_ID}/documents/{document_id}/signers"

    headers = {
        "X-Api-Key": API_KEY,
        "Content-Type": "application/json"
    }

    payload = {
        "signers": signers
    }

    response = requests.post(url, json=payload, headers=headers, timeout=30)

    print(f"Status: {response.status_code}")
    print(f"Response: {response.text[:500]}")

    if response.status_code == 200 or response.status_code == 201:
        data = response.json()
        print("✅ Envelope criado!")
        return data
    else:
        print("❌ Falha na criação do envelope")
        return None

if __name__ == "__main__":
    # Testar upload do relatório
    doc_id = upload_document("relatorio_testes_e2e.html")

    if doc_id:
        # Criar envelope com signatários
        signers = [
            {
                "email": "gabrielgfcramos2@gmail.com",
                "name": "Gabriel Ramos",
                "documentation": "CPF"
            }
        ]

        envelope = create_sign_envelope(doc_id, signers)

        if envelope:
            print("\n✅ Processo de assinatura iniciado via API!")
            print(f"📄 Document ID: {doc_id}")
            print(f"📧 Signatários notificados: {len(signers)}")
