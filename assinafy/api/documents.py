"""
Operações de documentos da API Assinafy.

Funções para upload, consulta e gerenciamento de documentos.
"""
import time
from typing import Any, Dict

import requests

from ..api.client import AssinafyClient
from ..config import AssinafyConfig
from ..logging_config import get_logger

logger = get_logger(__name__)


def upload_pdf(pdf_path: str, config: AssinafyConfig) -> Dict[str, Any]:
    """
    Fazer upload de PDF para a API Assinafy.

    Args:
        pdf_path: Caminho do arquivo PDF
        config: Configuração da API

    Returns:
        Dict com keys: id, status, signing_url, title

    Raises:
        FileNotFoundError: Se arquivo não existir
        ValueError: Se upload falhar
    """
    import os
    from pathlib import Path

    if not os.path.exists(pdf_path):
        raise FileNotFoundError(f"Arquivo não encontrado: {pdf_path}")

    logger.info(f"Iniciando upload: {Path(pdf_path).name}")
    logger.debug(f"Tamanho: {os.path.getsize(pdf_path) / 1024:.1f} KB")

    endpoint = f"/accounts/{config.workspace_id}/documents"

    client = AssinafyClient(config)
    response = client.upload_file(endpoint, pdf_path)

    logger.info(f"Status HTTP: {response.status_code}")

    if response.ok:
        try:
            data = response.json()
        except Exception as e:
            logger.error(f"Erro ao decodificar JSON: {e}")
            raise ValueError("Falha ao decodificar resposta da API")

        document_data = data.get('data', {})
        result = {
            'id': document_data.get('id'),
            'status': document_data.get('status'),
            'signing_url': document_data.get('signing_url'),
            'title': document_data.get('title', Path(pdf_path).stem)
        }

        logger.info(f"Upload realizado: {result['id']}")
        logger.debug(f"Status: {result['status']}")
        return result
    else:
        logger.error(f"Falha no upload: {response.text}")
        raise ValueError(f"Falha no upload: {response.text}")


def get_document(document_id: str, config: AssinafyConfig) -> Dict[str, Any]:
    """
    Obter detalhes de um documento.

    Args:
        document_id: ID do documento
        config: Configuração da API

    Returns:
        Dict com dados do documento

    Raises:
        ValueError: Se documento não for encontrado
    """
    logger.debug(f"Buscando documento: {document_id}")

    client = AssinafyClient(config)
    response = client.get(f"/documents/{document_id}")

    if response.status_code == 404:
        raise ValueError(f"Documento não encontrado: {document_id}")

    if response.ok:
        data = response.json()
        return data.get('data', {})
    else:
        raise ValueError(f"Erro ao buscar documento: {response.text}")


def wait_for_ready(
    document_id: str,
    config: AssinafyConfig,
    timeout: int = 60
) -> bool:
    """
    Aguardar documento ficar pronto para assinatura.

    Verifica status periodicamente até que documento esteja
    em um dos "ready_statuses" ou timeout.

    Args:
        document_id: ID do documento
        config: Configuração da API
        timeout: Timeout em segundos

    Returns:
        True se pronto, False se timeout ou erro
    """
    logger.info(f"Aguardando processamento: {document_id}")

    client = AssinafyClient(config)
    start_time = time.time()
    last_status = None

    while time.time() - start_time < timeout:
        try:
            response = client.get(f"/documents/{document_id}", timeout=10)

            if response.status_code != 200:
                logger.warning(f"Status {response.status_code}")
                time.sleep(config.polling_interval)
                continue

            data = response.json()
            document_data = data.get('data', {})
            status = document_data.get('status')

            if status != last_status:
                logger.info(f"Status: {status}")
                last_status = status

            if status in config.ready_statuses:
                logger.info("Documento pronto!")
                return True

            if status in config.processing_statuses:
                time.sleep(config.polling_interval)
                continue

            logger.warning(f"Status inesperado: {status}")
            return False

        except requests.RequestException as e:
            logger.error(f"Erro na requisição: {e}")
            time.sleep(config.polling_interval)
            continue

    logger.warning(f"Timeout após {timeout}s")
    return False


def list_documents(config: AssinafyConfig, limit: int = None) -> list:
    """
    Listar documentos do workspace.

    Args:
        config: Configuração da API
        limit: Limite de documentos (opcional)

    Returns:
        Lista de dicts com dados dos documentos
    """
    logger.debug("Listando documentos")

    client = AssinafyClient(config)
    response = client.get(f"/accounts/{config.workspace_id}/documents")

    if response.ok:
        data = response.json()
        documents = data.get('data', [])

        if limit:
            documents = documents[:limit]

        logger.debug(f"Encontrados: {len(documents)} documentos")
        return documents
    else:
        logger.error(f"Erro ao listar: {response.text}")
        return []
