import click
import json
from pathlib import Path
from src.scraper.extractor import DocumentationExtractor
from src.output.json_writer import JSONWriter


@click.group()
def cli():
    """Assinafy API Documentation Scraper"""
    pass


@cli.command()
@click.option('--output', '-o', type=click.Path(), default='data/assinafy_api.json', help='Caminho do arquivo de saída')
def scrape(output: str):
    """Scrapeia a documentação da API Assinafy e gera JSON estruturado"""
    click.echo("Iniciando scrape da documentação Assinafy...")

    extractor = DocumentationExtractor()

    with click.progressbar(length=100, label='Fetching pages') as bar:
        bar.update(50)
        try:
            docs = extractor.extract()
            bar.update(100)
        except Exception as e:
            click.echo(f"\nErro durante extração: {e}", err=True)
            raise

    total_endpoints = len(docs.get_all_endpoints())
    click.echo(f"\nExtraído: {len(docs.sections)} seções, {total_endpoints} endpoints")

    output_path = Path(output)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    writer = JSONWriter()
    writer.write(docs, str(output_path))

    file_size = output_path.stat().st_size
    click.echo(f"Salvo: {output_path} ({file_size:,} bytes)")

    if docs.metadata.get('source') == 'html_scraping':
        click.echo(f"Páginas processadas: {docs.metadata.get('pages_scraped', 0)}")


@cli.command()
@click.option('--input', '-i', type=click.Path(exists=True), default='data/assinafy_api.json', help='Arquivo JSON de entrada')
def info(input: str):
    """Mostra informações sobre o JSON extraído"""
    with open(input) as f:
        data = json.load(f)

    click.echo(f"Base URL: {data.get('base_url')}")
    click.echo(f"Extraído em: {data.get('extracted_at')}")
    click.echo(f"Fonte: {data.get('metadata', {}).get('source', 'unknown')}")

    sections = data.get('sections', [])
    click.echo(f"\nSeções ({len(sections)}):")

    total_endpoints = 0
    for section in sections:
        endpoints = section.get('endpoints', [])
        total_endpoints += len(endpoints)
        click.echo(f"  - {section['title']}: {len(endpoints)} endpoints")

    click.echo(f"\nTotal de endpoints: {total_endpoints}")


if __name__ == '__main__':
    cli()
