import json
import os
from pathlib import Path
from typing import Any, Dict, List

import click
from langchain_text_splitters import MarkdownHeaderTextSplitter


def initialize_text_splitter(
    split_config: Dict[str, Any]
) -> MarkdownHeaderTextSplitter:
    return MarkdownHeaderTextSplitter(
        headers_to_split_on=split_config["headers_to_split_on"],
    )


def split_by_config(
    data_filepaths: List[Path], split_config: Dict[str, Any]
) -> Dict[str, List[str]]:
    chunks_with_filenames = {}
    splitter = initialize_text_splitter(split_config)
    for data_filepath in data_filepaths:
        filename = data_filepath.name
        chunks = splitter.split_text(data_filepath.read_text())
        chunks = [chunk.page_content for chunk in chunks]
        chunks_with_filenames[filename] = chunks
    return chunks_with_filenames


@click.command()
@click.option("--data_dir", type=click.Path(exists=True))
@click.option("--split_config_path", type=click.Path(exists=True))
@click.option("--output_dir", type=click.Path(exists=False))
def main(data_dir: str, split_config_path: str, output_dir: str) -> None:
    """
    Read all txt files and split them according to the specified config.
    After that save the chunks in output directory

    Parameters
    ----------
    data_dir: str
        Path to the directory with txt files to split
    split_config_path: str
        Path to the json file with split config
    output_dir: str
        Path to the directory to save the chunks

    Returns
    -------
    None
    """
    data_dir: Path = Path(data_dir)
    output_dir: Path = Path(output_dir)

    os.makedirs(output_dir, exist_ok=True)
    with open(split_config_path, "r") as f:
        split_config = json.load(f)
    data_filepaths = list(data_dir.glob("*.txt"))
    chunks_with_filenames = split_by_config(data_filepaths, split_config)
    for input_filename, chunks in chunks_with_filenames.items():
        for i, chunk in enumerate(chunks):
            output_filepath = output_dir / f"{input_filename}_{i}.txt"
            output_filepath.write_text(chunk, "utf-8")
    return None


if __name__ == "__main__":
    main()