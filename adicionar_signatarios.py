#!/usr/bin/env python3
"""
Adicionar signatários ao documento via API Assinafy
"""
import os
import sys
import requests
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("ASSINAFY_API_KEY")
WORKSPACE_ID = os.getenv("ASSINAFY_WORKSPACE_ID")
BASE_URL = "https://api.assinafy.com.br/v1"

DOCUMENT_ID = "10235a92bf785028b2dbc45653ba"

SIGNER_EMAIL = "gabrielgfcramos2@gmail.com"
SIGNER_NAME = "Gabriel Ramos"

def add_signer_to_document():
    """Adicionar signatário ao documento"""
    print("="*60)
    print("✍️  Adicionar Signatário via API Assinafy")
    print("="*60)
    print(f"\n📄 Document ID: {DOCUMENT_ID}")
    print(f"👤 Signatário: {SIGNER_NAME} ({SIGNER_EMAIL})")
    print()

    # Endpoint para adicionar signatário
    url = f"{BASE_URL}/accounts/{WORKSPACE_ID}/documents/{DOCUMENT_ID}/signers"

    headers = {
        "X-Api-Key": API_KEY,
        "Content-Type": "application/json"
    }

    payload = {
        "signer": {
            "email": SIGNER_EMAIL,
            "name": SIGNER_NAME,
            "documentation": "CPF: 123.456.789-00"
        }
    }

    print("📡 Enviando requisição...")
    response = requests.post(url, json=payload, headers=headers, timeout=30)

    print(f"\n📊 Status HTTP: {response.status_code}")

    if response.status_code == 200 or response.status_code == 201:
        try:
            data = response.json()
        except:
            data = {}

        signer_data = data.get('data', {})
        signer_id = signer_data.get('id')
        status = signer_data.get('status', 'unknown')

        print(f"✅ Signatário adicionado com sucesso!")
        print(f"\n👤 Signer ID: {signer_id}")
        print(f"📌 Status: {status}")

        # Mostrar todos os dados
        print(f"\n📦 Dados completos:")
        print(f"   {signer_data}")

        return signer_id, signer_data

    else:
        print(f"❌ Falha ao adicionar signatário")
        print(f"\n📝 Response:")
        print(f"   {response.text}")

        return None, None

def get_signing_link():
    """Obter link de assinatura"""
    url = f"{BASE_URL}/accounts/{WORKSPACE_ID}/documents/{DOCUMENT_ID}"
    headers = {
        "X-Api-Key": API_KEY
    }

    response = requests.get(url, headers=headers, timeout=30)

    if response.status_code == 200:
        data = response.json()
        doc_data = data.get('data', {})
        signing_url = doc_data.get('signing_url')

        print(f"\n🔗 Link de Assinatura:")
        print(f"   {signing_url}")

        return signing_url

    return None

if __name__ == "__main__":
    # Adicionar signatário
    signer_id, signer_data = add_signer_to_document()

    if signer_id:
        print("\n" + "="*60)
        print("🎉 SUCESSO!")
        print("="*60)
        print(f"\n✅ Signatário adicionado ao documento!")

        # Obter link de assinatura
        signing_link = get_signing_link()

        print(f"\n💡 Próximos passos:")
        print(f"   1. O signatário receberá um email")
        print(f"   2. Ele pode assinar usando o link:")
        print(f"      {signing_link}")
        print(f"   3. Ou acessar: https://app.assinafy.com.br")
        print(f"   4. Buscar pelo documento e assinar")
