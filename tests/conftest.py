"""Fixtures compartilhadas para testes"""
import pytest
import logging
from types import SimpleNamespace


@pytest.fixture
def mock_config():
    """Mock de configuração Assinafy"""
    return SimpleNamespace(
        api_key="test_api_key",
        workspace_id="test_workspace_id",
        base_url="https://api.assinafy.com.br/v1",
        document_ready_timeout=60,
        polling_interval=2,
        ready_statuses=["metadata_ready", "pending_signature", "certificated"],
        processing_statuses=["uploaded", "uploading", "metadata_processing", "certificating"],
        log_level="INFO"
    )


@pytest.fixture
def clean_logging():
    """Resetar logging após testes"""
    # Salvar estado atual
    root_logger = logging.getLogger()
    original_handlers = root_logger.handlers[:]
    original_level = root_logger.level

    yield

    # Restaurar estado (mutar handlers, não rebind)
    root_logger.handlers.clear()
    root_logger.handlers.extend(original_handlers)
    root_logger.setLevel(original_level)
