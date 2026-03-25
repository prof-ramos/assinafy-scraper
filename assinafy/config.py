"""
Sistema de configuração centralizado para Assinafy scraper.

Carrega configuração de múltiplas fontes com precedência:
1. Variáveis de ambiente (mais prioritário)
2. Arquivo YAML (opcional)
3. Defaults hardcoded (menos prioritário)
"""
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

import yaml
from dotenv import load_dotenv


@dataclass
class AssinafyConfig:
    """Configuração centralizada do sistema Assinafy."""

    # API Configuration
    api_key: str
    workspace_id: str
    base_url: str = "https://api.assinafy.com.br/v1"

    # Document Processing
    document_ready_timeout: int = 60
    polling_interval: int = 2
    ready_statuses: list = field(default_factory=lambda: [
        "metadata_ready",
        "pending_signature",
        "certificated"
    ])
    processing_statuses: list = field(default_factory=lambda: [
        "uploaded",
        "uploading",
        "metadata_processing",
        "certificating"
    ])

    # Email Configuration
    email_template: str = "default"

    # Logging Configuration
    log_level: str = "INFO"
    log_file: Optional[Path] = None

    @classmethod
    def load(
        cls,
        config_path: Optional[Path] = None,
        env_file: Optional[Path] = None
    ) -> "AssinafyConfig":
        """
        Carregar configuração de múltiplas fontes.

        Args:
            config_path: Caminho para arquivo YAML de configuração (opcional)
            env_file: Caminho para arquivo .env (opcional, padrão: .env)

        Returns:
            Instância de AssinafyConfig carregada

        Raises:
            ValueError: Se campos obrigatórios estiverem faltando
        """
        # Carregar variáveis de ambiente do arquivo .env
        if env_file:
            load_dotenv(env_file)
        else:
            load_dotenv()

        # Configurações padrão
        config = {
            "base_url": "https://api.assinafy.com.br/v1",
            "document_ready_timeout": 60,
            "polling_interval": 2,
            "ready_statuses": [
                "metadata_ready",
                "pending_signature",
                "certificated"
            ],
            "processing_statuses": [
                "uploaded",
                "uploading",
                "metadata_processing",
                "certificating"
            ],
            "email_template": "default",
            "log_level": "INFO"
        }

        # Override com YAML se existir
        if config_path and config_path.exists():
            try:
                with open(config_path, "r") as f:
                    yaml_config = yaml.safe_load(f)
                    if yaml_config and "assinafy" in yaml_config:
                        config.update(yaml_config["assinafy"])
            except Exception as e:
                print(f"⚠️  Aviso: Erro ao ler config YAML: {e}")
                print("💡 Usando configurações padrão")

        # Override com variáveis de ambiente (credenciais sempre do env)
        api_key = os.getenv("ASSINAFY_API_KEY")
        workspace_id = os.getenv("ASSINAFY_WORKSPACE_ID")

        if not api_key:
            raise ValueError(
                "ASSINAFY_API_KEY não encontrado. "
                "Defina no arquivo .env ou como variável de ambiente."
            )

        if not workspace_id:
            raise ValueError(
                "ASSINAFY_WORKSPACE_ID não encontrado. "
                "Defina no arquivo .env ou como variável de ambiente."
            )

        config["api_key"] = api_key
        config["workspace_id"] = workspace_id

        # Override específicos do env se existirem
        if os.getenv("ASSINAFY_BASE_URL"):
            config["base_url"] = os.getenv("ASSINAFY_BASE_URL")

        # Converter Path para log_file se existir
        log_file_path = config.get("log_file")
        if log_file_path:
            config["log_file"] = Path(log_file_path)

        return cls(**config)

    def get_auth_headers(self, include_content_type: bool = True) -> dict:
        """
        Retornar headers de autenticação para requisições HTTP.

        Args:
            include_content_type: Incluir Content-Type (padrão: True)
                             Usar False para upload de arquivos (multipart)

        Returns:
            Dict de headers
        """
        headers = {
            "X-Api-Key": self.api_key,
            "Accept": "application/json"
        }

        if include_content_type:
            headers["Content-Type"] = "application/json"

        return headers
