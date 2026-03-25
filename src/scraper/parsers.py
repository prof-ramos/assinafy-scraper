from bs4 import BeautifulSoup, Tag
import re
import json
from typing import List, Tuple, Optional, Dict, Any
from .models import Endpoint, Parameter, HTTPMethod, ParameterType, Section


class DocumentationParser:
    BASE_URL = "https://api.assinafy.com.br/v1"

    def __init__(self, html: str):
        self.soup = BeautifulSoup(html, 'lxml')

    def extract_sections(self) -> List[Section]:
        sections = []

        for header in self.soup.find_all(re.compile('^h[1-6]$')):
            level = int(header.name[1])
            title = header.get_text().strip()

            content = []
            sibling = header.find_next_sibling()

            while sibling:
                if sibling.name and re.match('^h[1-6]$', sibling.name):
                    sibling_level = int(sibling.name[1])
                    if sibling_level <= level:
                        break
                content.append(str(sibling))
                sibling = sibling.find_next_sibling()

            section = Section(
                title=title,
                level=level,
                content=''.join(content) if content else None
            )
            sections.append(section)

        return sections

    def extract_curl_blocks(self) -> List[Tuple[Tag, Dict[str, Any]]]:
        curl_blocks = []

        for code_block in self.soup.find_all(['code', 'pre']):
            curl_text = code_block.get_text()
            if curl_text.strip().startswith('curl'):
                parsed = self._parse_curl_command(curl_text)
                if parsed:
                    curl_blocks.append((code_block, parsed))

        return curl_blocks

    def _parse_curl_command(self, curl: str) -> Optional[Dict[str, Any]]:
        method_match = re.search(r'-X\s+(GET|POST|PUT|PATCH|DELETE)', curl, re.IGNORECASE)
        method = method_match.group(1).upper() if method_match else 'GET'

        url_match = re.search(r'"(https://api\.assinafy\.com\.br/v1[^"]+)"', curl)
        if not url_match:
            url_match = re.search(r"'(https://api\.assinafy\.com\.br/v1[^']+)'", curl)

        if url_match:
            path = url_match.group(1).replace(self.BASE_URL, '')
        else:
            return None

        headers = {}
        for header_match in re.finditer(r'-H\s+"([^"]+)"', curl):
            header_text = header_match.group(1)
            if ':' in header_text:
                key, value = header_text.split(':', 1)
                headers[key.strip()] = value.strip()

        body = None
        body_match = re.search(r'-d\s+"([^"]+)"', curl)
        if body_match:
            try:
                body = json.loads(body_match.group(1))
            except json.JSONDecodeError:
                body = body_match.group(1)

        return {
            'method': method,
            'path': path,
            'headers': headers,
            'body': body
        }

    def extract_parameter_tables(self) -> List[List[Dict[str, str]]]:
        tables = []

        for table in self.soup.find_all('table'):
            thead = table.find('thead')
            if not thead:
                continue

            headers = [th.get_text().strip() for th in thead.find_all('th')]

            tbody = table.find('tbody')
            if not tbody:
                continue

            params = []
            for row in tbody.find_all('tr'):
                cells = [td.get_text().strip() for td in row.find_all(['td', 'th'])]
                if cells:
                    param_dict = dict(zip(headers, cells))
                    params.append(param_dict)

            if params:
                tables.append(params)

        return tables

    def extract_response_examples(self) -> List[Dict[str, Any]]:
        responses = []

        for code_block in self.soup.find_all(['code', 'pre']):
            class_attr = code_block.get('class', [])
            if any('json' in cls.lower() for cls in class_attr):
                try:
                    json_data = json.loads(code_block.get_text())
                    responses.append(json_data)
                except json.JSONDecodeError:
                    continue

        return responses

    def extract_endpoints(self) -> List[Endpoint]:
        endpoints = []

        curl_blocks = self.extract_curl_blocks()

        for code_block, curl_data in curl_blocks:
            endpoint = self._build_endpoint_from_curl(curl_data, code_block)
            if endpoint:
                endpoints.append(endpoint)

        return endpoints

    def _build_endpoint_from_curl(self, curl_data: Dict[str, Any], code_block: Tag) -> Optional[Endpoint]:
        method_str = curl_data.get('method', 'GET')
        try:
            method = HTTPMethod(method_str)
        except ValueError:
            return None

        path = curl_data.get('path', '/')

        prev_heading = code_block.find_previous(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
        title = prev_heading.get_text().strip() if prev_heading else f"{method} {path}"

        description = None
        next_p = code_block.find_next('p')
        if next_p:
            description = next_p.get_text().strip()

        parameters = []

        headers = curl_data.get('headers', {})
        for header_name, header_value in headers.items():
            param_type = ParameterType.HEADER
            required = header_name.lower() in ['x-api-key', 'authorization']

            param = Parameter(
                name=header_name,
                type='string',
                required=required,
                param_type=param_type,
                example=header_value if header_value and not header_value.startswith('xxx') else None
            )
            parameters.append(param)

        body = curl_data.get('body')
        request_example = body if isinstance(body, dict) else None

        response_example = None
        next_code = code_block.find_next(['code', 'pre'])
        if next_code:
            class_attr = next_code.get('class', [])
            if any('json' in cls.lower() for cls in class_attr):
                try:
                    response_example = json.loads(next_code.get_text())
                except json.JSONDecodeError:
                    pass

        requires_auth = any(
            p.name.lower() in ['x-api-key', 'authorization']
            for p in parameters
        )

        endpoint = Endpoint(
            title=title,
            method=method,
            path=path,
            description=description,
            parameters=parameters,
            request_example=request_example,
            response_example=response_example,
            requires_auth=requires_auth
        )

        return endpoint
