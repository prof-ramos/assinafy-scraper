"""
Módulo de envio de email com link de assinatura.

Abre cliente de email local com link mailto configurado.
"""
import urllib.parse
import webbrowser

from ..config import AssinafyConfig
from ..logging_config import get_logger

logger = get_logger(__name__)


def send_signing_email(
    document_id: str,
    signing_url: str,
    document_name: str,
    signer_email: str,
    signer_name: str,
    config: AssinafyConfig
) -> None:
    """
    Abrir cliente de email com rascunho de link de assinatura.

    Args:
        document_id: ID do documento
        signing_url: URL de assinatura
        document_name: Nome do documento
        signer_email: Email do signatário
        signer_name: Nome do signatário
        config: Configuração (para templates futuros)
    """
    logger.info(f"Preparando email para: {signer_email}")

    subject = f"📋 Documento para Assinatura Digital - {document_name}"

    body = f"""Olá {signer_name},

Segue o link para assinar digitalmente o documento "{document_name}":

🔗 Link de Assinatura:
{signing_url}

📋 Informações:
- Documento: {document_name}
- Document ID: {document_id}
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

    logger.debug("Abrindo cliente de email...")

    # Abrir cliente de email
    webbrowser.open(mailto_link)

    logger.info("Rascunho de email aberto")
