import json
from pathlib import Path
from ..scraper.models import Documentation


class JSONWriter:
    def write(self, docs: Documentation, output_path: str) -> None:
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)

        data = {
            'base_url': docs.base_url,
            'extracted_at': docs.extracted_at.isoformat(),
            'metadata': docs.metadata,
            'sections': [self._section_to_dict(s) for s in docs.sections]
        }

        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    def _section_to_dict(self, section) -> dict:
        return {
            'title': section.title,
            'level': section.level,
            'content': section.content,
            'subsections': [self._section_to_dict(s) for s in section.subsections],
            'endpoints': [self._endpoint_to_dict(e) for e in section.endpoints]
        }

    def _endpoint_to_dict(self, endpoint) -> dict:
        return {
            'title': endpoint.title,
            'method': endpoint.method.value,
            'path': endpoint.path,
            'description': endpoint.description,
            'parameters': [self._parameter_to_dict(p) for p in endpoint.parameters],
            'request_example': endpoint.request_example,
            'response_example': endpoint.response_example,
            'requires_auth': endpoint.requires_auth,
            'supports_pagination': endpoint.supports_pagination
        }

    def _parameter_to_dict(self, parameter) -> dict:
        return {
            'name': parameter.name,
            'type': parameter.type,
            'required': parameter.required,
            'description': parameter.description,
            'param_type': parameter.param_type.value,
            'example': parameter.example
        }
