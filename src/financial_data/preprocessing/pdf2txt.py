import os
from pathlib import Path

import click
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


@click.command()
@click.option(
    "--pdf_dir",
    type=click.Path(exists=True),
    help="Path to the PDF directory",
)
@click.option(
    "--txt_dir",
    type=click.Path(),
    help="Path to the txt directory",
)
def main(pdf_dir: str, txt_dir: str) -> None:
    """
    Convert PDF files to text files.

    Parameters:
    ----------
    pdf_path: str
        Path to the PDF directory.
    txt_dir: str
        Path to the txt directory.

    Returns:
    -------
    None
    """
    pdf_dir: Path = Path(pdf_dir)
    txt_dir: Path = Path(txt_dir)
    os.makedirs(txt_dir / "raw", exist_ok=True)
    for textbook_dir in pdf_dir.iterdir():
        if not textbook_dir.is_dir():
            continue
        pdf_file = get_pdf_file(textbook_dir, txt_dir)
        if pdf_file is None:
            continue
        raw_txt_file_path = txt_dir / "raw" / (textbook_dir.name + ".txt")
        convert_pdf_to_txt(pdf_file, raw_txt_file_path)
    return None


if __name__ == "__main__":
    main()
