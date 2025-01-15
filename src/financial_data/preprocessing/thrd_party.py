import json
from pathlib import Path
from typing import Dict, List
import uuid

from langchain_core.documents import Document
from langchain_text_splitters import (
    RecursiveCharacterTextSplitter,
)

from ..storages import (
    ChunkStorage,
    initialize_storage,
)


def process_3d_party_data() -> None:
    data_dir: Path = Path("./data/3d_party")
    chunk_storage = initialize_storage("chunk")

    for file in data_dir.iterdir():
        if file.is_file() and file.suffix == ".json":
            with open(file, "r") as f:
                data = json.load(f)
            actual_laws = get_relevant_laws(data)
            documents = transform_to_documents(actual_laws)
            for document in documents:
                document.metadata["source_name"] = file.name
            save_to_storage(chunk_storage, documents)
    return None


def get_relevant_laws(data: List[Dict[str, str]]) -> List[Dict[str, str]]:
    actual_codexes = ["Уголовный кодекс (УК РФ)"]
    return list(
        filter(lambda item: item["name_codex"] in actual_codexes, data)
    )


def transform_to_documents(
    data: List[Dict[str, str]],
    chunk_size: int = 1500,
) -> List[Document]:
    documents = []
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size, chunk_overlap=int(0.1 * chunk_size)
    )
    for item in data:
        content = item.pop("content_article")
        item["source"] = item["name_article"]
        item["id"] = str(uuid.uuid4())
        document = Document(content, metadata=item)
        documents.append(document)
    documents = splitter.split_documents(documents)
    return documents


def save_to_storage(
    chunk_storage: ChunkStorage, documents: List[Document]
) -> None:
    for document in documents:
        chunk_storage.set_chunk(document.metadata["id"], document)
    return None


if __name__ == "__main__":
    process_3d_party_data()
