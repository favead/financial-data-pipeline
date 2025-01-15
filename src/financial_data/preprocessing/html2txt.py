from pathlib import Path

import html2text
from prefect import flow, task

from ..storages import initialize_storage, DocumentStorage


@flow
def html2txt() -> None:
    """
    Convert html files to txt with md format
    """
    html_data_dirs = Path("./data/courses")
    document_storage = initialize_storage("document")

    h = html2text.HTML2Text()
    h.ignore_links = True
    h.ignore_images = True

    for data_dir in html_data_dirs.iterdir():
        for file in data_dir.iterdir():
            if not (file.suffix == ".html" or file.suffix == ".txt"):
                continue
            with open(file, "r") as f:
                content = f.read()
            transformed = h.handle(content)
            source_name = data_dir.name
            save_to_storage(document_storage, source_name, transformed)


@task
def save_to_storage(
    document_storage: DocumentStorage, source_name: str, document: str
) -> None:
    document_storage.set_raw_document(source_name, document)
    return None


if __name__ == "__main__":
    html2txt()
