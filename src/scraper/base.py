import requests
from typing import Optional, Dict
from bs4 import BeautifulSoup


class AssinafyScraper:
    BASE_URL = "https://api.assinafy.com.br/v1"
    DOCS_URL = f"{BASE_URL}/docs"

    def __init__(self, timeout: int = 30):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Assinafy-Scraper/1.0',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'pt-BR,pt;q=0.9,en;q=0.8',
        })
        self.timeout = timeout

    def fetch_documentation(self, path: str = "/docs") -> str:
        url = f"{self.BASE_URL}{path}"
        response = self.session.get(url, timeout=self.timeout)
        response.raise_for_status()
        return response.text

    def check_openapi_spec(self) -> Optional[str]:
        paths = [
            '/openapi.json',
            '/swagger.json',
            '/openapi.yaml',
            '/docs/openapi.json',
            '/api-docs',
        ]

        for path in paths:
            try:
                response = self.session.get(f"{self.BASE_URL}{path}", timeout=5)
                if response.status_code == 200:
                    return response.text
            except requests.RequestException:
                continue

        return None

    def fetch_all_pages(self) -> Dict[str, str]:
        openapi = self.check_openapi_spec()
        if openapi:
            return {'_openapi': openapi}

        pages = {'/docs': self.fetch_documentation('/docs')}

        soup = BeautifulSoup(pages['/docs'], 'html.parser')

        seen_paths = set(pages.keys())

        for link in soup.find_all('a', href=True):
            href = link['href']

            if href.startswith('/v1/docs/') or href.startswith('/docs/'):
                if href not in seen_paths:
                    try:
                        full_path = href if href.startswith('/') else f"/{href}"
                        pages[full_path] = self.fetch_documentation(full_path)
                        seen_paths.add(full_path)
                    except requests.RequestException as e:
                        print(f"Failed to fetch {href}: {e}")

        return pages
