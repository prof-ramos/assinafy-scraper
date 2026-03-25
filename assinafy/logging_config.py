"""
Configuração de logging estruturado para Assinafy scraper.

Formata logs com timestamp, level, module e line number.
Suporta output em console e arquivo.
"""
import logging
import sys
from pathlib import Path
from typing import Optional


# Formato padrão de logging
DEFAULT_FORMAT = "[%(asctime)s] %(levelname)-8s [%(name)s:%(lineno)d] %(message)s"
DEFAULT_DATEFMT = "%Y-%m-%d %H:%M:%S"


def setup_logging(
    level: str = "INFO",
    log_file: Optional[Path] = None,
    format_string: Optional[str] = None
) -> None:
    """
    Configurar logging para toda a aplicação.

    Args:
        level: Nível de logging (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Caminho opcional para arquivo de log
        format_string: Format string customizado (opcional)
    """
    # Converter level string para constante do logging
    log_level = getattr(logging, level.upper(), logging.INFO)

    # Usar formato padrão ou customizado
    fmt = format_string or DEFAULT_FORMAT
    datefmt = DEFAULT_DATEFMT

    # Criar formatter
    formatter = logging.Formatter(fmt, datefmt)

    # Configurar console handler (stdout)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)
    console_handler.setFormatter(formatter)

    # Configurar root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)

    # Remover handlers existentes para evitar duplicatas
    root_logger.handlers.clear()

    # Adicionar console handler
    root_logger.addHandler(console_handler)

    # Adicionar file handler se especificado
    if log_file:
        # Criar diretório se não existir
        log_file.parent.mkdir(parents=True, exist_ok=True)

        file_handler = logging.FileHandler(log_file, encoding="utf-8")
        file_handler.setLevel(logging.DEBUG)  # Arquivo sempre DEBUG
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)


def get_logger(name: str) -> logging.Logger:
    """
    Obter logger configurado para um módulo.

    Args:
        name: Nome do módulo (geralmente __name__)

    Returns:
        Logger configurado

    Example:
        >>> from assinafy.logging_config import get_logger
        >>> logger = get_logger(__name__)
        >>> logger.info("Mensagem informativa")
    """
    return logging.getLogger(name)


def log_level_from_verbosity(verbose_count: int) -> str:
    """
    Converter contagem de verbosidade para nível de logging.

    Args:
        verbose_count: Número de flags -v (0, 1, 2, ...)

    Returns:
        String de nível de logging

    Example:
        >>> log_level_from_verbosity(0)
        'WARNING'
        >>> log_level_from_verbosity(1)
        'INFO'
        >>> log_level_from_verbosity(2)
        'DEBUG'
        >>> log_level_from_verbosity(3)  # >= 2 também retorna DEBUG
        'DEBUG'
    """
    if verbose_count == 0:
        return "WARNING"
    elif verbose_count == 1:
        return "INFO"
    else:
        return "DEBUG"
