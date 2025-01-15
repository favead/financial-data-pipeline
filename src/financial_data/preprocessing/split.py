from typing import Any, Dict, List
import uuid

from langchain_core.documents import Document
from langchain_text_splitters import (
    MarkdownHeaderTextSplitter,
    RecursiveCharacterTextSplitter,
)

from ..storages import ChunkStorage, initialize_storage


SPLIT_CONFIG = {
    "headers_to_split_on": [
        ["#", "H1"],
        ["##", "H2"],
        ["###", "H3"],
        ["####", "H4"],
        ["#####", "H5"],
        ["######", "H6"],
        ["#######", "H7"],
        ["########", "H8"],
    ]
}


class ChunkSplitter:
    def __init__(
        self,
        chunk_size: int,
    ) -> None:
        self.text_splitter = RecursiveCharacterTextSplitter(
            separators=["."],
            chunk_size=chunk_size,
            chunk_overlap=int(0.15 * chunk_size),
        )

    def split(
        self, text_data: str, splitter_config: Dict[str, Any]
    ) -> List[Document]:
        md_splitter = self._get_md_splitter(splitter_config)
        documents = md_splitter.split_text(text_data)
        documents = self.text_splitter.split_documents(documents)
        return documents

    def _get_md_splitter(
        self, splitter_config: Dict[str, Any]
    ) -> MarkdownHeaderTextSplitter:
        return MarkdownHeaderTextSplitter(**splitter_config)


def split_documents() -> None:
    """
    Split documents from /data/to_split directory to chunks
    and store it in /data/chunks
    """
    document_storage = initialize_storage("document")
    chunk_storage = initialize_storage("chunk")
    processed_documents = document_storage.get_processed_documents()
    chunks_meta: Dict[str, List[Document]] = get_chunks_with_metadata(
        processed_documents
    )
    for _, chunk_docs in chunks_meta.items():
        save_to_storage(chunk_storage, chunk_docs)
    return None


def get_chunks_with_metadata(
    processed_documents: List[str],
    chunk_size: int = 2500,
) -> Dict[str, List[Document]]:
    splitter = ChunkSplitter(chunk_size)
    chunks_meta = {}
    for document in processed_documents:
        if document["source_name"] not in chunks_meta:
            chunks_meta[document["source_name"]] = []
        chunks = splitter.split(document["content"], SPLIT_CONFIG)
        for chunk in chunks:
            chunk.metadata["source_name"] = document["source_name"]
            chunk.metadata["id"] = str(uuid.uuid4())
        chunks_meta[document["source_name"]].extend(chunks)
    return chunks_meta


def save_to_storage(
    chunk_storage: ChunkStorage, chunks: List[Document]
) -> None:
    for chunk in chunks:
        chunk_storage.set_chunk(chunk.metadata["id"], chunk)
    return None


if __name__ == "__main__":
    split_documents()
