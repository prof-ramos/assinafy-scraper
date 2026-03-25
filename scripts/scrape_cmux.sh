#!/bin/bash
set -e

cd "$(dirname "$0")/.."

cmux log "Iniciando scrape Assinafy..."

cmux set-progress 0.0 --label "Instalando dependências"
uv sync

cmux set-status phase "Scraping documentação" --icon "🕷️"
cmux set-progress 0.3

uv run python -m src.cli scrape

cmux set-status phase "Concluído" --icon "✅"
cmux set-progress 1.0
cmux log "Arquivo gerado: data/assinafy_api.json"

cmux clear-status phase
cmux clear-progress
