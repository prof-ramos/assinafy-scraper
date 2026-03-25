#!/usr/bin/env python3
"""
Verificar estrutura da API Assinafy para Signers/Assignments

Usa o documento criado para entender o fluxo correto.
"""
import json

with open('data/assinafy_api.json') as f:
    docs = json.load(f)

print("🔍 Buscando endpoints relacionados a Signers/Assignments...\n")

# Buscar endpoints com "sign" no título
for section in docs['sections']:
    for endpoint in section['endpoints']:
        if 'sign' in endpoint['title'].lower():
            print(f"Found: {endpoint['method']} {endpoint['path']}")
            print(f"  Title: {endpoint['title']}")

print("\n" + "="*60)
print("📋 Documentos já criados:")
print("="*60)

# Usar a API para listar documentos
import os
import requests
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("ASSINAFY_API_KEY")
WORKSPACE_ID = os.getenv("ASSINAFY_WORKSPACE_ID")
BASE_URL = "https://api.assinafy.com.br/v1"

url = f"{BASE_URL}/accounts/{WORKSPACE_ID}/documents"
headers = {"X-Api-Key": API_KEY}

response = requests.get(url, headers=headers, timeout=30)

if response.status_code == 200:
    data = response.json()
    docs = data.get('data', [])

    for i, doc in enumerate(docs[:6], 1):
        doc_id = doc.get('id')
        status = doc.get('status')
        has_signing_url = 'signing_url' in doc

        print(f"{i}. ID: {doc_id}")
        print(f"   Status: {status}")
        print(f"   Signing URL: {'✅' if has_signing_url else '❌'}")

        if has_signing_url:
            print(f"   Link: {doc['signing_url']}")
        print()
