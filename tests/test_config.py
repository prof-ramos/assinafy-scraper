"""Testes unitários para o módulo de configuração"""
import os
import pytest

from assinafy.config import AssinafyConfig


class TestAssinafyConfig:
    """Testes para AssinafyConfig"""

    def test_load_with_env_vars(self):
        """Testar carregamento com variáveis de ambiente"""
        # Este teste assume que .env existe com credenciais válidas
        # Em ambiente de CI, seria necessário mockar

        # Verificar se variáveis de ambiente existem
        api_key = os.getenv("ASSINAFY_API_KEY")
        workspace_id = os.getenv("ASSINAFY_WORKSPACE_ID")

        if not api_key or not workspace_id:
            pytest.skip("Variáveis de ambiente não configuradas")

        # Carregar configuração
        config = AssinafyConfig.load()

        # Verificar campos obrigatórios
        assert config.api_key == api_key
        assert config.workspace_id == workspace_id

        # Verificar defaults
        assert config.base_url == "https://api.assinafy.com.br/v1"
        assert config.document_ready_timeout == 60
        assert config.polling_interval == 2

    def test_direct_instantiation(self):
        """Testar instanciação direta da config"""
        # Criar config diretamente
        config = AssinafyConfig(
            api_key="test_key",
            workspace_id="test_ws"
        )

        assert config.api_key == "test_key"
        assert config.workspace_id == "test_ws"
        assert config.base_url == "https://api.assinafy.com.br/v1"
        assert config.document_ready_timeout == 60
        assert config.polling_interval == 2

    def test_get_auth_headers_with_content_type(self):
        """Testar headers de autenticação com Content-Type"""
        config = AssinafyConfig(
            api_key="test_key",
            workspace_id="test_ws"
        )

        headers = config.get_auth_headers(include_content_type=True)

        assert headers["X-Api-Key"] == "test_key"
        assert headers["Accept"] == "application/json"
        assert headers["Content-Type"] == "application/json"

    def test_get_auth_headers_without_content_type(self):
        """Testar headers de autenticação sem Content-Type (para uploads)"""
        config = AssinafyConfig(
            api_key="test_key",
            workspace_id="test_ws"
        )

        headers = config.get_auth_headers(include_content_type=False)

        assert headers["X-Api-Key"] == "test_key"
        assert headers["Accept"] == "application/json"
        assert "Content-Type" not in headers

    def test_ready_statuses_default(self):
        """Testar statuses de pronto default"""
        config = AssinafyConfig(
            api_key="test_key",
            workspace_id="test_ws"
        )

        expected_statuses = ["metadata_ready", "pending_signature", "certificated"]
        assert config.ready_statuses == expected_statuses

    def test_processing_statuses_default(self):
        """Testar statuses de processamento default"""
        config = AssinafyConfig(
            api_key="test_key",
            workspace_id="test_ws"
        )

        expected_statuses = ["uploaded", "uploading", "metadata_processing", "certificating"]
        assert config.processing_statuses == expected_statuses

