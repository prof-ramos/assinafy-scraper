#!/usr/bin/env python3
"""
Wrapper script para CLI do Assinafy scraper.

Uso: python assinafy_cli.py [comando] [opções]
     ./assinafy_cli.py [comando] [opções]  (após chmod +x)
"""
import sys

from assinafy.cli import cli

if __name__ == "__main__":
    try:
        cli()
    except KeyboardInterrupt:
        print("\nInterrupted by user", file=sys.stderr)
        sys.exit(0)
    except Exception as err:
        print(f"Erro: {err}", file=sys.stderr)
        sys.exit(1)
