from itertools import islice
from typing import Iterable, Iterator, TypeVar, Optional, Any

from langchain_core.documents import Document
from langchain_core.indexing.api import _deduplicate_in_order, _hash_string_to_uuid, _adelete
from pydantic import model_validator

from ai_native_core.indexing.de_duplication import de_duplicator
from ai_native_core.indexing.splitter import split_docs, split_tools
from ai_native_core.indexing.weaviate_client import weaviate_client
from ai_native_core.utils.vector_store import get_vector_store

T = TypeVar("T")


def _batch(size: int, iterable: Iterable[T]) -> Iterator[list[T]]:
    """Utility batching function."""
    it = iter(iterable)
    while True:
        chunk = list(islice(it, size))
        if not chunk:
            return
        yield chunk


class _HashedDocument(Document):
    """A hashed document with a unique ID."""

    uid: str
    hash_: str
    """The hash of the document including content and metadata."""
    content_hash: str
    """The hash of the document content."""
    metadata_hash: str
    """The hash of the document metadata."""

    @classmethod
    def is_lc_serializable(cls) -> bool:
        return False

    @model_validator(mode="before")
    @classmethod
    def calculate_hashes(cls, values: dict[str, Any]) -> Any:
        """Root validator to calculate content and metadata hash."""
        content = values.get("page_content", "")
        metadata = values.get("metadata", {})

        forbidden_keys = ("hash_", "content_hash", "metadata_hash")

        for key in forbidden_keys:
            if key in metadata:
                msg = (
                    f"Metadata cannot contain key {key} as it "
                    f"is reserved for internal use."
                )
                raise ValueError(msg)

        content_hash = str(_hash_string_to_uuid(content))

        values["content_hash"] = content_hash
        values['metadata_hash'] = ''
        values["hash_"] = content_hash

        _uid = values.get("uid")

        if _uid is None:
            values["uid"] = values["hash_"]
        return values

    def to_document(self) -> Document:
        """Return a Document object."""
        return Document(
            id=self.uid,
            page_content=self.page_content,
            metadata=self.metadata,
        )

    @classmethod
    def from_document(
            cls, document: Document, *, uid: Optional[str] = None
    ):
        """Create a HashedDocument from a Document."""
        # noinspection PyArgumentList
        return cls(  # type: ignore[call-arg]
            uid=uid,  # type: ignore[arg-type]
            page_content=document.page_content,
            metadata=document.metadata,
        )


async def index(
        document_id: str,
        tenant: str,
        namespace: str,
        doc: Document,
        batch_size: int = 100,
        knowledge_type: str = "common",
):
    """
    内容新增+内容更新
    :param document_id: 文章id
    :param tenant: 租户id
    :param namespace: 命名空间id
    :param doc: 源markdown文档
    :param batch_size: 吞吐量
    :param knowledge_type: 知识类型：1.常规知识 2.工具知识
    :return:
    """
    if knowledge_type == "common":
        docs_source = split_docs(
            markdown_documents=[doc]
        )
    elif knowledge_type == "tool":
        docs_source = split_tools(
            tool_doc=doc
        )
    else:
        raise ValueError(f"Unsupported knowledge type: {knowledge_type}")
    vector_store = get_vector_store(
        tenant=tenant,
        namespace=namespace,
        knowledge_type=knowledge_type
    )

    doc_iterator = iter(docs_source)
    all_to_add_ids = []
    all_to_delete_ids = []
    for doc_batch in _batch(batch_size, doc_iterator):
        hashed_docs = list(
            _deduplicate_in_order(
                [_HashedDocument.from_document(doc) for doc in doc_batch]
            )
        )
        source_ids = [
            doc.uid for doc in hashed_docs
        ]
        to_add_ids, to_delete_ids = await de_duplicator.get_to_update_and_to_delete_doc_ids(
            document_id=document_id,
            source_ids=source_ids,
        )
        to_add_docs = []
        to_add_uids = []
        for doc, source_id in zip(hashed_docs, source_ids):
            if source_id in to_add_ids:
                to_add_docs.append(doc.to_document())
                to_add_uids.append(source_id)

        if to_add_docs:
            res = await vector_store.aadd_documents(
                to_add_docs,
                ids=to_add_uids,
                batch_size=batch_size,
            )
        if to_delete_ids:
            await _adelete(vector_store, list(to_delete_ids))
        await de_duplicator.update_source_ids(
            document_id=document_id,
            to_add_ids=list(to_add_ids),
            to_delete_ids=list(to_delete_ids),
        )
        all_to_add_ids.extend(
            to_add_ids
        )
        all_to_delete_ids.extend(
            to_delete_ids
        )
    return all_to_add_ids, all_to_delete_ids


async def delete(
        document_id: str,
        tenant: str,
        namespace: str,
        knowledge_type: str = "common",
):
    """
    删除文章
    :param document_id: 文章id
    :param tenant: 租户id
    :param namespace: 命名空间id
    :param knowledge_type: 知识类型：1.常规知识 2.工具知识
    :return:
    """
    vector_store = get_vector_store(
        tenant=tenant,
        namespace=namespace,
        knowledge_type=knowledge_type
    )
    source_ids = await de_duplicator.redis_client.smembers(document_id)
    await _adelete(vector_store, source_ids)
    await de_duplicator.delete(document_id)


async def update_meta_data(
        document_id: str,
        tenant: str,
        namespace: str,
        meta_data_map: dict,
        knowledge_type: str = "common"
):
    """
    更新文章元数据
    :param document_id: 文章id
    :param tenant: 租户id
    :param namespace: 命名空间id
    :param meta_data_map: 文章元数据
    :param knowledge_type: 知识类型：1.常规知识 2.工具知识
    :return:
    """
    source_ids = await de_duplicator.get_all_source_ids(document_id)
    if knowledge_type == "common":
        jeopardy = weaviate_client.collections.get(f"common_knowledge_{tenant}_{namespace}")
    elif knowledge_type == "tool":
        jeopardy = weaviate_client.collections.get(f"tool_knowledge_{tenant}_{namespace}")
    else:
        raise ValueError(f"Unsupported knowledge type: {knowledge_type}")
    for source_id in source_ids:
        # Update the object with the new properties
        jeopardy.data.update(
            uuid=source_id,
            properties=meta_data_map
        )
