"""Testes unitários para CLI"""
import pytest
from click.testing import CliRunner
from unittest.mock import patch, MagicMock

from assinafy.cli import cli


class TestCLI:
    """Testes para CLI Assinafy"""

    @pytest.fixture
    def runner(self):
        """Criar CliRunner"""
        return CliRunner()

    @pytest.fixture
    def mock_config(self):
        """Mock de configuração"""
        config = MagicMock()
        config.api_key = "test_key"
        config.workspace_id = "test_ws"
        config.base_url = "https://api.assinafy.com.br/v1"
        return config

    def test_cli_help(self, runner):
        """Testar --help"""
        result = runner.invoke(cli, ["--help"])
        assert result.exit_code == 0
        assert "CLI para automação de assinaturas Assinafy" in result.output
        assert "automate" in result.output
        assert "upload" in result.output
        assert "send-link" in result.output

    def test_cli_automate_help(self, runner):
        """Testar automate --help"""
        result = runner.invoke(cli, ["automate", "--help"])
        assert result.exit_code == 0
        assert "Automatizar fluxo completo de assinatura" in result.output
        assert "--email" in result.output
        assert "--name" in result.output

    def test_cli_upload_help(self, runner):
        """Testar upload --help"""
        result = runner.invoke(cli, ["upload", "--help"])
        assert result.exit_code == 0
        assert "Fazer upload de PDF" in result.output
        assert "PDF_PATH" in result.output

    def test_cli_send_link_help(self, runner):
        """Testar send-link --help"""
        result = runner.invoke(cli, ["send-link", "--help"])
        assert result.exit_code == 0
        assert "Enviar link de assinatura" in result.output
        assert "DOCUMENT_ID" in result.output
        assert "--email" in result.output

    def test_verbose_flag(self, runner, mock_config):
        """Testar flag --verbose"""
        with patch("assinafy.cli.AssinafyConfig.load", return_value=mock_config):
            # Testar -v (INFO)
            result = runner.invoke(cli, ["-v", "upload", "--help"])
            assert result.exit_code == 0

            # Testar --verbose (forma longa)
            result = runner.invoke(cli, ["--verbose", "upload", "--help"])
            assert result.exit_code == 0

    def test_automate_command_missing_email(self, runner, mock_config):
        """Testar automate sem --email (deve falhar)"""
        with patch("assinafy.cli.AssinafyConfig.load", return_value=mock_config):
            # Criar arquivo PDF temporário
            with runner.isolated_filesystem():
                with open("test.pdf", "wb") as f:
                    f.write(b"PDF content")

                result = runner.invoke(cli, ["automate", "test.pdf"])
                assert result.exit_code != 0
                assert "Missing option" in result.output or "--email" in result.output

    def test_upload_command_missing_file(self, runner, mock_config):
        """Testar upload com arquivo inexistente"""
        with patch("assinafy.cli.AssinafyConfig.load", return_value=mock_config):
            result = runner.invoke(cli, ["upload", "nonexistent.pdf"])
            assert result.exit_code != 0
            assert "does not exist" in result.output

    def test_send_link_missing_document_id(self, runner, mock_config):
        """Testar send-link sem DOCUMENT_ID"""
        with patch("assinafy.cli.AssinafyConfig.load", return_value=mock_config):
            result = runner.invoke(cli, ["send-link"])
            assert result.exit_code != 0
            assert "Missing argument" in result.output
