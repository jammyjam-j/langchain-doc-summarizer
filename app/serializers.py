from typing import Any, Dict, List

from app.models import Document
from app.schemas import DocumentResponse


class BaseSerializer:
    def serialize(self, obj: Any) -> Dict[str, Any]:
        raise NotImplementedError

    def serialize_many(self, objs: List[Any]) -> List[Dict[str, Any]]:
        return [self.serialize(obj) for obj in objs]


class DocumentSerializer(BaseSerializer):
    def serialize(self, doc: Document) -> Dict[str, Any]:
        data = {
            "id": doc.id,
            "title": doc.title,
            "content": doc.content,
            "created_at": doc.created_at.isoformat(),
            "updated_at": doc.updated_at.isoformat(),
        }
        return data

    def to_response(self, doc: Document) -> DocumentResponse:
        return DocumentResponse(**self.serialize(doc))

    def to_responses(self, docs: List[Document]) -> List[DocumentResponse]:
        return [self.to_response(d) for d in docs]


def serialize_document(document: Document) -> Dict[str, Any]:
    serializer = DocumentSerializer()
    return serializer.serialize(document)


def serialize_documents(documents: List[Document]) -> List[Dict[str, Any]]:
    serializer = DocumentSerializer()
    return serializer.serialize_many(documents)