import enum
from typing import Optional, List

from pydantic import Field

from appodus_utils import Object


class DocumentAccessScope(str, enum.Enum):
    PRIVATE = "private"
    PUBLIC = "public"
    INTERNAL = "internal"


class CreateDocumentDto(Object):
    store_key: str
    access_scope: DocumentAccessScope
    store_bucket: Optional[str] = None
    tags: Optional[List[str]] = None
    owner: Optional[str] = None
    description: Optional[str] = None


class DocumentMetadata(Object):
    tags: List[str] = Field(default_factory=list)
    owner: Optional[str] = None
    description: Optional[str] = None


class FileDto(Object):
    url: str
    document_id: str
