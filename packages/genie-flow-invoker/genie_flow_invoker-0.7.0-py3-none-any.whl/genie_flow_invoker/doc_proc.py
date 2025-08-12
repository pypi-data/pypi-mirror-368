import base64
import io
import uuid
from typing import Optional, Iterator, Literal, Union
from typing_extensions import TypeAliasType

from pydantic import BaseModel, Field, model_validator

CustomPropertyType = TypeAliasType(
    "CustomPropertyType",
    "Union[bool, int, float, str, uuid.UUID, None, dict[str, CustomPropertyType], list[CustomPropertyType]]"
)
NAMESPACE_DOC_PROC = uuid.UUID("e3bf4d4c-068e-11f0-aa96-000d3a0b8a34")


class AbstractNamedDocument(BaseModel):
    filename: str = Field(
        description="The filename that has been given to this file",
    )


class RawDocumentFile(AbstractNamedDocument):
    document_data: str = Field(
        description="A base64 encoded version of the document data of this file",
    )

    @property
    def byte_io(self):
        buffer = base64.b64decode(self.document_data)
        return io.BytesIO(buffer)


class DocumentChunk(BaseModel):
    chunk_id: Optional[str] = Field(
        default=None,
        description="The ID of the document chunk, if not given it will be set to uuid5 of content",
    )

    @model_validator(mode='before')
    def pre_init(cls, values):
        content = values.get("content", None) or ""
        chunk_id = values.get("chunk_id", str(uuid.uuid5(NAMESPACE_DOC_PROC, content)))
        values["chunk_id"] = chunk_id
        return values

    content: str = Field(
        description="The chunk of text of a document",
    )
    original_span: tuple[int, int] = Field(
        description="The start and end position of the chunk in the original document",
    )
    hierarchy_level: int = Field(
        description="The level of hierarchy that this chunk belongs to",
    )
    custom_properties: Optional[dict[str, CustomPropertyType]] = Field(
        default=None,
        description="A dictionary of custom properties that will be stored with this chunk",
    )
    parent_id: Optional[str] = Field(
        description="The ID of an optional upward related chunk",
    )
    embedding: Optional[list[float]] = Field(
        default=None,
        description="The embedding of the chunk",
    )


class ChunkedDocument(AbstractNamedDocument):
    document_metadata: Optional[dict] = Field(
        None,
        description="The optional document metadata dictionary",
    )
    chunks: list[DocumentChunk] = Field(
        description="The list of chunks of this document",
    )

    def chunk_iterator(self, operation_level: Optional[int]) -> Iterator[DocumentChunk]:
        """
        Returns an iterator over the chunks of this document, optionally at a certain
        operation level. If the level is specified, only the chunks with a corresponding
        hierarchy level are returned. If the level is None, all chunks are returned. If the
        level is negative, the operation level is calculated from the loweste level to the
        top. Minus one then being the lowest level, minus two the level above that, etc.

        :param operation_level: indicator what level of the hierarchy of chunks should be
        returned
        :return: an iterator over the chunks of this document
        """
        if operation_level is not None and operation_level < 0:
            max_level_chunk = max(self.chunks, key=lambda x: x.hierarchy_level)
            operation_level = max_level_chunk.hierarchy_level + operation_level + 1

        for chunk in self.chunks:
            if (
                operation_level is None
                or chunk.hierarchy_level == operation_level
            ):
                yield chunk


class ChunkDistance(BaseModel):
    chunk: DocumentChunk = Field(
        description="The retrieved chunk",
    )
    distance: float = Field(
        description="The distance of the chunk towards search query",
    )


DistanceMethodType = Literal["cosine", "euclidian", "manhattan"]


class SimilaritySearchRequest(AbstractNamedDocument):
    include_vector: bool = Field(
        default=False,
        description="Include vectors in the resulting chunks",
    )
    method: DistanceMethodType = Field(
        default="cosine",
        description="The similarity search method",
    )
    parent_strategy: Optional[str] = Field(
        default=None,
        description="The strategy used to determine how to include parents of result chunks",
    )
    top: Optional[int] = Field(
        default=None,
        description="The maximum number of similarity search results to return",
    )
    horizon: Optional[float] = Field(
        default=None,
        description="The horizon of the similarity search query",
    )
    operation_level: Optional[int] = Field(
        default=None,
        description="The level of hierarchy that the search operation should be conducted",
    )
    query_embedding: list[float] = Field(
        description="The embedding of the similarity search query",
    )
