"""
This script converts a PDF file to a text file and processes the text data.
"""

import os
from pathlib import Path
import click

import pymupdf4llm


def convert_pdf_to_txt(pdf_file_path: Path, txt_file_path: Path) -> None:
    """Convert PDF file to text file."""
    print(f"Converting {pdf_file_path} to {txt_file_path}")
    with open(txt_file_path, "wb") as f:
        md_data = pymupdf4llm.to_markdown(pdf_file_path)
        f.write(md_data.encode("utf-8"))
    return None


@click.command()
@click.option("--pdf_path", type=click.Path(exists=True), required=True)
@click.option("--txt_path", type=click.Path(), required=True)
def main(pdf_path: str, txt_path: str) -> None:
    txt_path = Path(txt_path)
    os.makedirs(txt_path / "raw", exist_ok=True)
    os.makedirs(txt_path / "processed", exist_ok=True)

    # Iterate through textbook directories
    for textbook_dir in Path(pdf_path).iterdir():
        if not textbook_dir.is_dir():
            continue

        # Find PDF file in textbook directory
        pdf_files = list(textbook_dir.glob("*.pdf"))
        if not pdf_files:
            continue
        pdf_file_path = pdf_files[0]
        raw_txt_file_path = (
            txt_path / "raw" / pdf_file_path.with_suffix(".txt").name
        )
        convert_pdf_to_txt(pdf_file_path, raw_txt_file_path)


if __name__ == "__main__":
    main()
