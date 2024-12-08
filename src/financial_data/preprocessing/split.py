import json
import os
from pathlib import Path
from typing import Any, Dict, List, Union

from langchain_core.load import dumpd
from langchain_core.documents import Document
from langchain_text_splitters import (
    MarkdownHeaderTextSplitter,
    HTMLSectionSplitter,
)
from transformers import AutoTokenizer


class ChunkSplitter:
    def __init__(
        self,
        min_size: int,
        model_path: str,
    ) -> None:
        self.tokenizer = AutoTokenizer.from_pretrained(model_path)
        self.min_size = min_size

    def split(
        self, filepath: Path, splitter_config: Dict[str, Any]
    ) -> List[Document]:
        _, file_ext = os.path.splitext(str(filepath))
        md_splitter = self._get_md_splitter(file_ext, splitter_config)
        with open(filepath, "r") as f:
            filedata = f.read()
        documents = md_splitter.split_text(filedata)
        return documents

    def _get_md_splitter(
        self, file_ext: str, splitter_config: Dict[str, Any]
    ) -> Union[MarkdownHeaderTextSplitter, HTMLSectionSplitter]:
        return MarkdownHeaderTextSplitter(**splitter_config)

    def squeeze_chunks(self, documents: List[Document]) -> List[Document]:
        squeezed_chunks = []
        temp_document = Document("")
        for document in documents:
            chunk = document.page_content
            tokens = self.tokenizer.tokenize(chunk)
            n_tokens = len(tokens)
            if n_tokens < self.min_size:
                temp_document.page_content = (
                    (temp_document.page_content + "\n" + chunk).strip()
                    if temp_document.page_content
                    else chunk
                )
            else:
                if (
                    temp_document.page_content
                    and len(temp_document.page_content) > self.min_size
                ):
                    squeezed_chunks.append(temp_document)
                    temp_document = Document("")
                squeezed_chunks.append(document)

        if temp_document.page_content:
            squeezed_chunks.append(temp_document)
        return squeezed_chunks


def split_documents_by_dir(
    data_dir: Path,
    min_size: int = 300,
    model_path: str = "intfloat/multilingual-e5-large",
) -> None:
    splitter = ChunkSplitter(min_size, model_path)
    chunks_meta = {}
    for files_dir in data_dir.iterdir():
        dirname = files_dir.name
        chunks_meta[dirname] = []
        splitter_config_path = list(files_dir.glob("*.json"))
        assert len(splitter_config_path) == 1
        with open(splitter_config_path[0], "r") as f:
            splitter_config = json.load(f)
        for filepath in files_dir.iterdir():
            if filepath.is_file() and filepath.suffix != ".json":
                chunks = splitter.split(filepath, splitter_config)
                chunks_meta[dirname].extend(chunks)

        chunks_meta[dirname] = splitter.squeeze_chunks(chunks_meta[dirname])
    return chunks_meta


def split_documents() -> None:
    """
    Split documents from /data/to_split directory to chunks
    and store it in /data/chunks
    """
    model_path = "intfloat/multilingual-e5-small"
    data_dir: Path = Path("./data/test")
    output_dir: Path = Path("./data/chunks")
    chunks_meta = split_documents_by_dir(data_dir, model_path=model_path)
    documents = []
    for dirname, chunk_docs in chunks_meta.items():
        with open(output_dir / f"{dirname}.json", "w") as f:
            json.dump({"documents": dumpd(chunk_docs)}, f)
        documents.extend(chunk_docs)
    return None


if __name__ == "__main__":
    split_documents()
