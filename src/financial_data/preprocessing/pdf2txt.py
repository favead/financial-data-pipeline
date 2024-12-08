import os
from pathlib import Path

import pymupdf4llm


def convert_pdf_to_txt(pdf_file_path: Path, txt_file_path: Path) -> None:
    """
    Convert PDF file to text file in markdown format via pymupdf4llm.

    Parameters:
    ----------
    pdf_file_path: Path
        Path to the PDF file.
    txt_file_path: Path
        Path to the text file.

    Returns:
    -------
    None
    """
    print(f"Converting {pdf_file_path} to {txt_file_path}")
    with open(txt_file_path, "wb") as f:
        md_data = pymupdf4llm.to_markdown(pdf_file_path)
        f.write(md_data.encode("utf-8"))
    return None


def get_pdf_file(textbook_dir: Path, raw_txt_path: Path) -> Path | None:
    """
    Extract pdf file from textbook directory.
    It is guaranteed that there is only one pdf file in the textbook directory.

    Parameters:
    ----------
    textbook_dir: Path
        Path to the textbook directory.
    raw_txt_path: Path
        Path to the raw text directory.

    Returns:
    -------
    Path | None
        Path to the pdf file if found, None otherwise.
    """
    # Find PDF file in textbook directory
    pdf_files = list(textbook_dir.glob("*.pdf"))
    if not pdf_files:
        return None
    pdf_file_path = pdf_files[0]
    return pdf_file_path


def pdf2txt() -> None:
    """
    Convert PDF files to text files.
    """
    pdf_dir: Path = Path("./data/pdf_textbooks")
    txt_dir: Path = Path("./data/txt_data")
    for i, textbook_dir in enumerate(pdf_dir.iterdir()):
        if not textbook_dir.is_dir():
            continue
        pdf_file = get_pdf_file(textbook_dir, txt_dir)
        if pdf_file is None:
            continue
        txt_file_dir = txt_dir / textbook_dir.name
        os.makedirs(txt_file_dir, exist_ok=True)
        raw_txt_file_path = txt_file_dir / f"{i}.txt"
        convert_pdf_to_txt(pdf_file, raw_txt_file_path)
    return None


if __name__ == "__main__":
    pdf2txt()
