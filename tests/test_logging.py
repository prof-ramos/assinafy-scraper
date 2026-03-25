"""Testes unitários para o módulo de logging"""
import logging
import re
import pytest
from pathlib import Path

from assinafy.logging_config import setup_logging, get_logger


class TestLoggingConfig:
    """Testes para configuração de logging"""

    def test_setup_logging_default(self, clean_logging):
        """Testar setup_logging com configurações padrão"""
        setup_logging()

        root_logger = logging.getLogger()
        assert root_logger.level == logging.INFO
        assert len(root_logger.handlers) > 0

    @pytest.mark.parametrize("level,expected_log_level", [
        ("DEBUG", logging.DEBUG),
        ("WARNING", logging.WARNING),
    ])
    def test_setup_logging_levels(self, clean_logging, level, expected_log_level):
        """Testar setup_logging com diferentes níveis de log"""
        setup_logging(level=level)

        root_logger = logging.getLogger()
        assert root_logger.level == expected_log_level

    def test_setup_logging_with_file(self, clean_logging, tmp_path):
        """Testar setup_logging com arquivo de log"""
        log_file = tmp_path / "test.log"

        setup_logging(level="INFO", log_file=log_file)

        root_logger = logging.getLogger()

        # Verificar se há pelo menos 2 handlers (console + file)
        assert len(root_logger.handlers) >= 2

        # Verificar se existe um FileHandler
        file_handlers = [h for h in root_logger.handlers if isinstance(h, logging.FileHandler)]
        assert len(file_handlers) >= 1

        # Escrever um log e verificar se foi salvo no arquivo
        logger = get_logger("test")
        logger.info("Test message")

        # Flush handlers (não fechar)
        for handler in root_logger.handlers:
            handler.flush()

        # Verificar conteúdo do arquivo
        content = log_file.read_text()
        assert "Test message" in content

    def test_get_logger(self, clean_logging):
        """Testar get_logger"""
        setup_logging()

        logger = get_logger("test_module")
        assert logger.name == "test_module"
        assert isinstance(logger, logging.Logger)

    def test_logger_output_format(self, clean_logging, capsys):
        """Testar formato de output do logger"""
        setup_logging(level="INFO")

        logger = get_logger("test_module")
        logger.info("Test message")

        # Capturar stdout
        captured = capsys.readouterr()
        assert "Test message" in captured.out

        # Verificar formato de timestamp: [YYYY-MM-DD HH:MM:SS]
        # Regex para timestamp no formato esperado
        timestamp_pattern = r"\[\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\]"
        assert re.search(timestamp_pattern, captured.out), f"Timestamp não encontrado em: {captured.out}"

    def test_multiple_loggers(self, clean_logging):
        """Testar múltiplos loggers"""
        setup_logging(level="DEBUG")

        logger1 = get_logger("module1")
        logger2 = get_logger("module2")

        assert logger1.name == "module1"
        assert logger2.name == "module2"

        # Ambos devem compartilhar o mesmo root logger
        assert logger1.parent == logger2.parent
