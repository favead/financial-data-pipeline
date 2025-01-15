from pathlib import Path

from prefect import flow, task
import pymupdf4llm

from ..storages import DocumentStorage, initialize_storage
from ..utils.log import get_logger


log = get_logger(__name__)


@flow
def pdf2txt() -> None:
    """
    Convert PDF files to text files.
    """
    pdf_dir: Path = Path("./data/pdf_textbooks")
    document_storage = initialize_storage("document")

    for textbook_dir in pdf_dir.iterdir():
        if not textbook_dir.is_dir():
            continue
        pdf_file = get_pdf_file(textbook_dir)
        if pdf_file is None:
            continue
        md_data = convert_pdf_to_txt(pdf_file)
        save_to_storage(document_storage, str(textbook_dir.name), md_data)
    return None


@task
def get_pdf_file(textbook_dir: Path) -> Path | None:
    """
    Extract pdf file from textbook directory.
    It is guaranteed that there is only one pdf file in the textbook directory.
    """
    # Find PDF file in textbook directory
    pdf_files = list(textbook_dir.glob("*.pdf"))
    if not pdf_files:
        return None
    pdf_file_path = pdf_files[0]
    return pdf_file_path


@task
def convert_pdf_to_txt(pdf_file_path: Path) -> str:
    """
    Convert PDF file to text file in markdown format via pymupdf4llm.
    """
    log.info(f"Converting {pdf_file_path}")
    md_data = pymupdf4llm.to_markdown(pdf_file_path)
    return md_data


@task
def save_to_storage(
    document_storage: DocumentStorage, source_name: str, raw_txt_file_path: str
) -> None:
    """
    Save txt data to document storage
    """
    with open(raw_txt_file_path, "r", encoding="utf-8") as f:
        data = f.read()
        document_storage.set_raw_document(source_name, data)
    return None


if __name__ == "__main__":
    pdf2txt()
