from typing import List, Dict
from .base import AssinafyScraper
from .parsers import DocumentationParser
from .models import Documentation, Section, Endpoint


class DocumentationExtractor:
    def __init__(self):
        self.scraper = AssinafyScraper()

    def extract(self) -> Documentation:
        pages = self.scraper.fetch_all_pages()

        if '_openapi' in pages:
            return self._parse_openapi(pages['_openapi'])

        all_sections = []
        all_endpoints = []

        for path, html in pages.items():
            parser = DocumentationParser(html)

            sections = parser.extract_sections()
            all_sections.extend(sections)

            endpoints = parser.extract_endpoints()
            all_endpoints.extend(endpoints)

        organized_sections = self._organize_sections(all_sections, all_endpoints)

        return Documentation(
            base_url=self.scraper.BASE_URL,
            sections=organized_sections,
            metadata={
                'source': 'html_scraping',
                'pages_scraped': len(pages),
                'total_endpoints': len(all_endpoints)
            }
        )

    def _organize_sections(self, sections: List[Section], endpoints: List[Endpoint]) -> List[Section]:
        section_map = {}
        root_sections = []

        for section in sections:
            section_map[section.title] = section

        for endpoint in endpoints:
            normalized_path = endpoint.normalize_path()

            for section_title, section in section_map.items():
                if section_title.lower() in normalized_path.lower():
                    section.endpoints.append(endpoint)
                    break
            else:
                if root_sections:
                    root_sections[0].endpoints.append(endpoint)

        for section in sections:
            if section.endpoints:
                for endpoint in section.endpoints:
                    endpoint.path = endpoint.normalize_path()

        level_1_sections = [s for s in sections if s.level == 1]

        if not level_1_sections:
            return sections

        return level_1_sections

    def _parse_openapi(self, spec: str) -> Documentation:
        import json

        try:
            spec_dict = json.loads(spec)
        except json.JSONDecodeError:
            return Documentation(
                base_url=self.scraper.BASE_URL,
                sections=[],
                metadata={'source': 'openapi_parse_error'}
            )

        sections = []
        paths = spec_dict.get('paths', {})

        for path, methods in paths.items():
            for method, details in methods.items():
                if method.lower() not in ['get', 'post', 'put', 'patch', 'delete']:
                    continue

                endpoint = Endpoint(
                    title=details.get('summary', f"{method.upper()} {path}"),
                    method=method.upper(),
                    path=path,
                    description=details.get('description'),
                    parameters=[],
                    requires_auth=True
                )

                tag = details.get('tags', [None])[0]
                if tag:
                    section = next((s for s in sections if s.title == tag), None)
                    if not section:
                        section = Section(title=tag, level=1)
                        sections.append(section)
                    section.endpoints.append(endpoint)

        return Documentation(
            base_url=spec_dict.get('servers', [{'url': self.scraper.BASE_URL}])[0]['url'],
            sections=sections,
            metadata={'source': 'openapi_spec'}
        )
