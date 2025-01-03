import json
from pathlib import Path
from typing import Dict, List

from langchain_core.documents import Document
from langchain_text_splitters import (
    RecursiveCharacterTextSplitter,
)
from prefect import flow, task

from ..utils.jsonl import save_documents_to_jsonl


@flow
def process_3d_party_data() -> None:
    data_dir: Path = Path("./data/3d_party")
    output_dir: Path = Path("./data/chunks")

    for file in data_dir.iterdir():
        if file.is_file() and file.suffix == ".json":
            with open(file, "r") as f:
                data = json.load(f)
            actual_laws = get_relevant_laws(data)
            documents = transform_to_documents(actual_laws)
            for document in documents:
                document.metadata["source"] = file.name
            save_documents_to_jsonl(
                documents, output_dir / f"{file.stem}.jsonl"
            )
    return None


@task
def get_relevant_laws(data: List[Dict[str, str]]) -> List[Dict[str, str]]:
    actual_codexes = ["Уголовный кодекс (УК РФ)"]
    return list(
        filter(lambda item: item["name_codex"] in actual_codexes, data)
    )


@task
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
        document = Document(content, metadata=item)
        documents.append(document)
    documents = splitter.split_documents(documents)
    return documents


if __name__ == "__main__":
    process_3d_party_data()
