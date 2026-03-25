#!/usr/bin/env python3
"""
Testar diferentes métodos de upload via API Assinafy

O objetivo é automatizar o processo de assinatura digital.
"""
import os
import sys
import requests
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("ASSINAFY_API_KEY")
WORKSPACE_ID = os.getenv("ASSINAFY_WORKSPACE_ID")
BASE_URL = "https://api.assinafy.com.br/v1"

def test_upload_html():
    """Test 1: Tentar upload de HTML direto"""
    print("📤 Test 1: Upload HTML direto")

    url = f"{BASE_URL}/accounts/{WORKSPACE_ID}/documents"

    # Criar um HTML simples
    html_content = """
    <!DOCTYPE html>
    <html>
    <head><title>Teste</title></head>
    <body><h1>Documento de Teste</h1></body>
    </html>
    """

    files = {
        'file': ('test.html', html_content, 'text/html')
    }
    headers = {
        "X-Api-Key": API_KEY
    }

    response = requests.post(url, files=files, headers=headers, timeout=30)

    print(f"Status: {response.status_code}")
    print(f"Response: {response.text[:200]}")

    return response.status_code == 200 or response.status_code == 201

def test_upload_text():
    """Test 2: Tentar upload como texto/plain"""
    print("\n📤 Test 2: Upload como texto/plain")

    url = f"{BASE_URL}/accounts/{WORKSPACE_ID}/documents"

    text_content = "Documento de teste para assinatura digital."

    files = {
        'file': ('test.txt', text_content, 'text/plain')
    }
    headers = {
        "X-Api-Key": API_KEY
    }

    response = requests.post(url, files=files, headers=headers, timeout=30)

    print(f"Status: {response.status_code}")
    print(f"Response: {response.text[:200]}")

    return response.status_code == 200 or response.status_code == 201

def test_multipart_upload():
    """Test 3: Tentar upload com multipart/form-data"""
    print("\n📤 Test 3: Upload multipart/form-data")

    url = f"{BASE_URL}/accounts/{WORKSPACE_ID}/documents"

    # Criar multipart data
    files = {
        'file': ('test.txt', 'Conteúdo do documento', 'text/plain')
    }
    data = {
        'title': 'Documento Teste',
        'description': 'Documento para testar upload via API'
    }
    headers = {
        "X-Api-Key": API_KEY
    }

    response = requests.post(url, files=files, data=data, headers=headers, timeout=30)

    print(f"Status: {response.status_code}")
    print(f"Response: {response.text[:200]}")

    return response.status_code == 200 or response.status_code == 201

def test_create_document_from_url():
    """Test 4: Criar documento a partir de URL"""
    print("\n📤 Test 4: Criar documento a partir de URL")

    url = f"{BASE_URL}/accounts/{WORKSPACE_ID}/documents"

    # Supondo que o HTML está hospedado
    data = {
        'url': 'file:///Users/gabrielramos/Documents/Programas/assinafy-scraper/relatorio_testes_e2e.html',
        'title': 'Relatório de Testes E2E'
    }
    headers = {
        "X-Api-Key": API_KEY,
        "Content-Type": "application/json"
    }

    response = requests.post(url, json=data, headers=headers, timeout=30)

    print(f"Status: {response.status_code}")
    print(f"Response: {response.text[:200]}")

    return response.status_code == 200 or response.status_code == 201

def test_list_documents():
    """Test 5: Listar documentos existentes"""
    print("\n📋 Test 5: Listar documentos existentes")

    url = f"{BASE_URL}/accounts/{WORKSPACE_ID}/documents"
    headers = {
        "X-Api-Key": API_KEY
    }

    response = requests.get(url, headers=headers, timeout=30)

    print(f"Status: {response.status_code}")

    if response.status_code == 200:
        data = response.json()
        docs = data.get('data', [])
        print(f"✅ Documentos encontrados: {len(docs)}")

        for doc in docs[:3]:  # Primeiros 3
            doc_id = doc.get('id')
            title = doc.get('title', 'Sem título')
            status = doc.get('status', 'unknown')
            print(f"   - {title} ({doc_id}) - Status: {status}")

        return docs
    else:
        print(f"❌ Falha: {response.text}")
        return []

if __name__ == "__main__":
    print("="*60)
    print("🔍 INVESTIGANDO MÉTODOS DE UPLOAD - API Assinafy")
    print("="*60)
    print()

    # Primeiro listar documentos existentes
    existing_docs = test_list_documents()

    print("\n" + "-"*60)
    print("TESTANDO DIFERENTES MÉTODOS DE UPLOAD")
    print("-"*60)
    print()

    # Testar diferentes métodos
    methods = [
        ("HTML direto", test_upload_html),
        ("Texto plano", test_upload_text),
        ("Multipart", test_multipart_upload),
        ("From URL", test_create_document_from_url),
    ]

    results = []
    for name, test_func in methods:
        try:
            success = test_func()
            results.append((name, success))
        except Exception as e:
            print(f"❌ Erro: {e}")
            results.append((name, False))

    print("\n" + "="*60)
    print("📊 RESUMO DOS TESTES")
    print("="*60)
    print()

    for name, success in results:
        status = "✅" if success else "❌"
        print(f"{status} {name}")

    print("\n💡 RECOMENDAÇÃO:")
    print("Use o método manual via plataforma Assinafy:")
    print("1. Acesse: https://assinafy.com.br")
    print("2. Faça upload do relatorio_testes_e2e.html")
    print("3. Adicione signatários")
    print("4. Envie para coleta de assinaturas")
