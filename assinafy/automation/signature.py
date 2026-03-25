"""
Módulo de automação de assinatura digital.

Orquestra o fluxo completo de upload, aguardo de processamento
e envio de link de assinatura via email.
"""
from pathlib import Path

from ..api.documents import get_document, upload_pdf, wait_for_ready
from ..automation.email import send_signing_email
from ..config import AssinafyConfig
from ..logging_config import get_logger

logger = get_logger(__name__)


def automate_signature(
    pdf_path: str,
    signer_email: str,
    config: AssinafyConfig,
    signer_name: str = None,
    document_name: str = None,
    timeout: int = 60
) -> dict:
    """
    Automatizar fluxo completo de assinatura digital.

    Orquestra: upload → aguardar processamento → enviar email

    Args:
        pdf_path: Caminho do arquivo PDF
        signer_email: Email do signatário
        config: Configuração com dados da API
        signer_name: Nome do signatário (opcional)
        document_name: Nome do documento (opcional)
        timeout: Timeout para aguardar processamento (padrão: 60)

    Returns:
        Dict com keys: document_id, signing_url
    """
    # Usar nome do arquivo como document_name se não fornecido
    if not document_name:
        document_name = Path(pdf_path).stem

    # Usar email como nome se signer_name não fornecido
    if not signer_name:
        signer_name = signer_email.split('@')[0]

    logger.info("="*60)
    logger.info("FLUXO COMPLETO DE AUTOMAÇÃO DE ASSINATURA")
    logger.info("="*60)
    logger.info(f"Arquivo: {pdf_path}")
    logger.info(f"Signatário: {signer_name} ({signer_email})")
    logger.info(f"Documento: {document_name}")

    # Passo 1: Upload do PDF
    logger.info("Passo 1: Upload do PDF")
    upload_result = upload_pdf(pdf_path, config)

    document_id = upload_result['id']
    signing_url = upload_result['signing_url']

    # Passo 2: Aguardar processamento do documento
    logger.info("Passo 2: Aguardando processamento")
    ready = wait_for_ready(document_id, config, timeout)

    if not ready:
        logger.warning("Documento não ficou pronto a tempo")
        logger.info("Email será enviado mesmo assim")

    # Passo 3: Enviar email com link de assinatura
    logger.info("Passo 3: Enviar email com link de assinatura")
    send_signing_email(
        document_id=document_id,
        signing_url=signing_url,
        document_name=document_name,
        signer_email=signer_email,
        signer_name=signer_name,
        config=config
    )

    return {
        'document_id': document_id,
        'signing_url': signing_url
    }


def automate_signature(
    pdf_path: str,
    signer_email: str,
    config: AssinafyConfig,
    signer_name: str = None,
    document_name: str = None,
    timeout: int = 60
) -> dict:
    """
    Automatizar fluxo completo de assinatura digital.

    Orquestra: upload → aguardar processamento → enviar email

    Args:
        pdf_path: Caminho do arquivo PDF
        signer_email: Email do signatário
        config: Configuração com dados da API
        signer_name: Nome do signatário (opcional)
        document_name: Nome do documento (opcional)
        timeout: Timeout para aguardar processamento (padrão: 60)

    Returns:
        Dict com keys: document_id, signing_url
    """
    # Usar nome do arquivo como document_name se não fornecido
    if not document_name:
        document_name = Path(pdf_path).stem

    # Usar email como nome se signer_name não fornecido
    if not signer_name:
        signer_name = signer_email.split('@')[0]

    logger.info("="*60)
    logger.info("FLUXO COMPLETO DE AUTOMAÇÃO DE ASSINATURA")
    logger.info("="*60)
    logger.info(f"Arquivo: {pdf_path}")
    logger.info(f"Signatário: {signer_name} ({signer_email})")
    logger.info(f"Documento: {document_name}")

    # Passo 1: Upload do PDF
    logger.info("Passo 1: Upload do PDF")
    upload_result = upload_pdf(pdf_path, config)

    document_id = upload_result['id']
    signing_url = upload_result['signing_url']

    # Passo 2: Aguardar processamento do documento
    logger.info("Passo 2: Aguardando processamento")
    ready = wait_for_document_ready(document_id, config, timeout)

    if not ready:
        logger.warning("Documento não ficou pronto a tempo")
        logger.info("Email será enviado mesmo assim")

    # Passo 3: Enviar email com link de assinatura
    logger.info("Passo 3: Enviar email com link de assinatura")
    send_signing_email(
        document_id=document_id,
        signing_url=signing_url,
        document_name=document_name,
        signer_email=signer_email,
        signer_name=signer_name,
        config=config
    )

    return {
        'document_id': document_id,
        'signing_url': signing_url
    }
