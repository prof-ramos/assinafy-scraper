"""
CLI principal para automação de assinaturas Assinafy.

Command group principal com subcomandos para:
- automate: Fluxo completo de automação
- upload: Upload de PDF
- send-link: Enviar link de assinatura
"""
import click

from .config import AssinafyConfig
from .logging_config import setup_logging, log_level_from_verbosity


@click.group()
@click.option(
    "--verbose", "-v",
    count=True,
    help="Aumentar verbosidade (-v=INFO, -vv=DEBUG)"
)
@click.option(
    "--config", "-c",
    type=click.Path(exists=True),
    help="Arquivo YAML de configuração"
)
@click.pass_context
def cli(ctx, verbose, config):
    """
    CLI para automação de assinaturas Assinafy.

    Exemplo de uso:

      \b
      assinafy automate documento.pdf --email user@example.com

    Para ver ajuda de um comando específico:

      \b
      assinafy COMANDO --help
    """
    ctx.ensure_object(dict)

    # Configurar logging baseado na verbosidade
    level = log_level_from_verbosity(verbose)
    setup_logging(level=level)

    # Carregar configuração
    try:
        ctx.obj["config"] = AssinafyConfig.load(
            config_path=click.Path(config).resolve() if config else None
        )
        ctx.obj["verbose"] = verbose
    except ValueError as e:
        click.echo(f"❌ Erro de configuração: {e}", err=True)
        ctx.exit(1)


@cli.command()
@click.argument("pdf_path", type=click.Path(exists=True))
@click.option(
    "--email", "-e",
    required=True,
    help="Email do signatário"
)
@click.option(
    "--name", "-n",
    help="Nome do signatário"
)
@click.option(
    "--document-name", "-d",
    help="Nome do documento"
)
@click.option(
    "--timeout",
    type=int,
    default=60,
    help="Timeout em segundos para aguardar processamento (padrão: 60)"
)
@click.pass_context
def automate(ctx, pdf_path, email, name, document_name, timeout):
    """
    Automatizar fluxo completo de assinatura digital.

    Fluxo:
      1. Upload do PDF
      2. Aguardar processamento (opcional)
      3. Enviar email com link de assinatura

    Exemplo:

      \b
      assinafy automate documento.pdf --email user@example.com --name "User Name"
    """
    from .automation.signature import automate_signature

    config = ctx.obj["config"]

    # Se document_name não fornecido, usar nome do arquivo
    if not document_name:
        from pathlib import Path
        document_name = Path(pdf_path).stem

    result = automate_signature(
        pdf_path=pdf_path,
        signer_email=email,
        signer_name=name,
        document_name=document_name,
        config=config,
        timeout=timeout
    )

    click.echo("\n" + "="*60)
    click.echo("✅ FLUXO COMPLETO CONCLUÍDO!")
    click.echo("="*60)
    click.echo(f"\n📄 Document ID: {result['document_id']}")
    click.echo(f"🔗 Signing URL: {result['signing_url']}")
    click.echo(f"👤 Signatário: {name or email} ({email})")


@cli.command()
@click.argument("pdf_path", type=click.Path(exists=True))
@click.pass_context
def upload(ctx, pdf_path):
    """
    Fazer upload de PDF para a Assinafy.

    Retorna o document_id e signing_url.

    Exemplo:

      \b
      assinafy upload documento.pdf
    """
    from .api.documents import upload_pdf

    config = ctx.obj["config"]

    result = upload_pdf(pdf_path, config=config)

    click.echo(f"Document ID: {result['id']}")
    click.echo(f"Signing URL: {result['signing_url']}")


@cli.command()
@click.argument("document_id")
@click.option(
    "--email", "-e",
    required=True,
    help="Email do signatário"
)
@click.option(
    "--name", "-n",
    help="Nome do signatário"
)
@click.pass_context
def send_link(ctx, document_id, email, name):
    """
    Enviar link de assinatura para signatário.

    Abre o cliente de email com um rascunho contendo o link.

    Exemplo:

      \b
      assinafy send-link DOCUMENT_ID --email user@example.com
    """
    from .automation.email import send_signing_email

    config = ctx.obj["config"]

    # Buscar documento para obter dados
    from .api.documents import get_document

    doc = get_document(document_id, config=config)
    document_name = doc.get("title", "Documento")

    send_signing_email(
        document_id=document_id,
        signing_url=doc.get("signing_url"),
        document_name=document_name,
        signer_email=email,
        signer_name=name
    )

    click.echo("✅ Rascunho de email aberto no cliente de email")
    click.echo(f"💡 Revise e envie para {email}")
