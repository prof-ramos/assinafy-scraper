#!/usr/bin/env python3
"""
Testar upload de PDF específico via API Assinafy

⚠️ Este script é mantido para compatibilidade reversa.
   Para uso novo, prefira: assinafy_cli.py upload
"""
import os
import sys
import requests
from dotenv import load_dotenv

from assinafy.logging_config import setup_logging, get_logger

load_dotenv()

# Configurar logging
setup_logging(level="INFO")
logger = get_logger(__name__)

API_KEY = os.getenv("ASSINAFY_API_KEY")
WORKSPACE_ID = os.getenv("ASSINAFY_WORKSPACE_ID")
BASE_URL = "https://api.assinafy.com.br/v1"

if not API_KEY or not WORKSPACE_ID:
    logger.error("Credenciais não encontradas")
    sys.exit(1)

# Aceitar arquivo via linha de comando
if len(sys.argv) < 2:
    logger.error("Uso: python test_upload_pdf.py <caminho_para_pdf>")
    sys.exit(1)

PDF_FILE = sys.argv[1]

if not os.path.exists(PDF_FILE):
    logger.error(f"Arquivo não encontrado: {PDF_FILE}")
    sys.exit(1)

def upload_pdf():
    """Fazer upload do PDF via API Assinafy"""
    logger.info("="*60)
    logger.info("Upload de PDF via API Assinafy")
    logger.info("="*60)
    logger.info(f"Arquivo: {PDF_FILE}")
    logger.info(f"Tamanho: {os.path.getsize(PDF_FILE) / 1024:.1f} KB")
    logger.info(f"Workspace: {WORKSPACE_ID}")

    url = f"{BASE_URL}/accounts/{WORKSPACE_ID}/documents"

    with open(PDF_FILE, 'rb') as f:
        files = {
            'file': (os.path.basename(PDF_FILE), f, 'application/pdf')
        }
        headers = {
            "X-Api-Key": API_KEY
        }

        logger.info("Enviando requisição...")
        response = requests.post(url, files=files, headers=headers, timeout=30)

    logger.info(f"Status HTTP: {response.status_code}")

    if response.status_code == 200 or response.status_code == 201:
        try:
            data = response.json()
        except:
            data = {}

        document_data = data.get('data', {})
        document_id = document_data.get('id')
        title = document_data.get('title', 'Sem título')
        status = document_data.get('status', 'unknown')

        logger.info("Upload realizado com sucesso!")
        logger.info(f"Document ID: {document_id}")
        logger.debug(f"Título: {title}")
        logger.debug(f"Status: {status}")

        # Manter print para output final de dados
        print(f"📄 Document ID: {document_id}")
        print(f"📋 Título: {title}")
        print(f"📌 Status: {status}")
        print(f"\n📦 Dados completos:")
        print(f"   {document_data}")

        return document_id, document_data

    else:
        logger.error("Falha no upload")
        logger.error(f"Response: {response.text}")
        return None, None

def list_all_documents():
    """Listar todos os documentos do workspace"""
    logger.info("="*60)
    logger.info("Documentos no Workspace")
    logger.info("="*60)

    url = f"{BASE_URL}/accounts/{WORKSPACE_ID}/documents"
    headers = {
        "X-Api-Key": API_KEY
    }

    response = requests.get(url, headers=headers, timeout=30)

    if response.status_code == 200:
        data = response.json()
        docs = data.get('data', [])

        logger.info(f"Total de documentos: {len(docs)}")

        for i, doc in enumerate(docs, 1):
            doc_id = doc.get('id')
            title = doc.get('title', 'Sem título')
            status = doc.get('status', 'unknown')
            created = doc.get('created_at', 'N/A')

            logger.info(f"{i}. {title} (ID: {doc_id}, Status: {status})")

            # Manter print para output visual
            print(f"{i}. {title}")
            print(f"   ID: {doc_id}")
            print(f"   Status: {status}")
            print(f"   Criado: {created}")
            print()
    else:
        logger.error(f"Falha ao listar: {response.text}")

if __name__ == "__main__":
    logger.info("="*60)
    logger.info("INICIANDO TESTE DE UPLOAD")
    logger.info("="*60)

    # Listar documentos antes
    list_all_documents()

    # Tentar upload
    doc_id, doc_data = upload_pdf()

    if doc_id:
        logger.info("="*60)
        logger.info("SUCESSO!")
        logger.info("="*60)
        logger.info("Documento foi adicionado ao workspace!")

        # Manter print para output final
        print("\n" + "="*60)
        print("🎉 SUCESSO!")
        print("="*60)
        print(f"\n📄 Documento foi adicionado ao workspace!")
        print(f"🔗 Para acessar: https://assinafy.com.br")
        print(f"\n💡 Próximos passos:")
        print(f"   1. Acesse o documento na plataforma")
        print(f"   2. Adicione signatários")
        print(f"   3. Envie para coleta de assinaturas")
