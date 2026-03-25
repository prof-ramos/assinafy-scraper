from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from enum import Enum
from datetime import datetime


class HTTPMethod(str, Enum):
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    PATCH = "PATCH"
    DELETE = "DELETE"


class ParameterType(str, Enum):
    HEADER = "header"
    QUERY = "query"
    PATH = "path"
    BODY = "body"


class Parameter(BaseModel):
    name: str
    type: str
    required: bool = False
    description: Optional[str] = None
    param_type: ParameterType
    example: Optional[Any] = None


class Endpoint(BaseModel):
    title: str
    method: HTTPMethod
    path: str
    description: Optional[str] = None
    parameters: List[Parameter] = []
    request_example: Optional[Dict[str, Any]] = None
    response_example: Optional[Dict[str, Any]] = None
    requires_auth: bool = True
    supports_pagination: bool = False

    def normalize_path(self) -> str:
        import re

        path = self.path
        # Substituir IDs MongoDB-like por placeholders
        path = re.sub(r'/[a-f0-9]{24,}', '/{id}', path)
        # Substituir UUIDs por placeholders
        path = re.sub(r'/[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}', '/{uuid}', path)
        # Substituir números sequenciais por placeholders
        path = re.sub(r'/\d{4,}', '/{id}', path)
        return path


class Section(BaseModel):
    title: str
    level: int
    content: Optional[str] = None
    subsections: List['Section'] = []
    endpoints: List[Endpoint] = []

    model_config = {"arbitrary_types_allowed": True}


class Documentation(BaseModel):
    base_url: str
    sections: List[Section] = []
    metadata: Dict[str, Any] = {}
    extracted_at: datetime = Field(default_factory=datetime.now)

    def get_all_endpoints(self) -> List[Endpoint]:
        endpoints = []
        for section in self.sections:
            endpoints.extend(section.endpoints)
            for subsection in section.subsections:
                endpoints.extend(subsection.endpoints)
        return endpoints
