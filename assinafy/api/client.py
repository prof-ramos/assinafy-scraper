"""
Cliente HTTP reutilizável para API Assinafy.

Gerencia sessão HTTP e headers de autenticação.
"""
import requests

from ..config import AssinafyConfig
from ..logging_config import get_logger

logger = get_logger(__name__)


class AssinafyClient:
    """
    Cliente HTTP para API Assinafy.

    Gerencia sessão requests.Session e headers de autenticação.
    """

    def __init__(self, config: AssinafyConfig):
        """
        Inicializar cliente.

        Args:
            config: Configuração com credenciais da API
        """
        self.config = config
        self.session = requests.Session()
        self.session.headers.update(config.get_auth_headers())

        logger.debug(f"Cliente inicializado: {config.base_url}")

    def get(self, endpoint: str, timeout: int = 30, **kwargs) -> requests.Response:
        """
        Fazer requisição GET.

        Args:
            endpoint: Endpoint da API (ex: /documents/{id})
            timeout: Timeout em segundos (padrão: 30)
            **kwargs: Argumentos adicionais para requests.get()

        Returns:
            Response object
        """
        url = f"{self.config.base_url}{endpoint}"
        logger.debug(f"GET {url}")

        response = self.session.get(url, timeout=timeout, **kwargs)
        logger.debug(f"Status: {response.status_code}")

        return response

    def post(
        self,
        endpoint: str,
        json: dict = None,
        data: dict = None,
        files: dict = None,
        timeout: int = 30,
        **kwargs
    ) -> requests.Response:
        """
        Fazer requisição POST.

        Args:
            endpoint: Endpoint da API
            json: Payload JSON
            data: Payload form-encoded
            files: Arquivos para upload (multipart/form-data)
            timeout: Timeout em segundos
            **kwargs: Argumentos adicionais

        Returns:
            Response object
        """
        url = f"{self.config.base_url}{endpoint}"
        logger.debug(f"POST {url}")

        response = self.session.post(
            url,
            json=json,
            data=data,
            files=files,
            timeout=timeout,
            **kwargs
        )
        logger.debug(f"Status: {response.status_code}")

        return response

    def upload_file(
        self,
        endpoint: str,
        file_path: str,
        file_type: str = "application/pdf",
        timeout: int = 30
    ) -> requests.Response:
        """
        Fazer upload de arquivo.

        Args:
            endpoint: Endpoint da API
            file_path: Caminho do arquivo local
            file_type: MIME type do arquivo
            timeout: Timeout em segundos

        Returns:
            Response object
        """
        import os
        from pathlib import Path

        path = Path(file_path)
        logger.debug(f"Upload: {file_path} ({os.path.getsize(file_path) / 1024:.1f} KB)")

        with open(file_path, 'rb') as f:
            files = {
                'file': (path.name, f, file_type)
            }

            # Remover Content-Type padrão e deixar requests definir
            headers = self.session.headers.copy()
            headers.pop('Content-Type', None)

            response = self.session.post(
                f"{self.config.base_url}{endpoint}",
                files=files,
                headers=headers,
                timeout=timeout
            )

        logger.debug(f"Upload status: {response.status_code}")
        return response
