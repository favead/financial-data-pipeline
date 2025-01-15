import os
from pathlib import Path

from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_community.vectorstores.faiss import DistanceStrategy

from ..storages import initialize_storage


MODEL_PATH = "intfloat/multilingual-e5-small"


def index_chunks() -> None:
    """
    Indexing chunks in directory and save it to FAISS database
    """
    output_dir = Path("./data/index")
    os.makedirs(output_dir, exist_ok=True)

    embeddings = HuggingFaceEmbeddings(
        model_name=MODEL_PATH,
        multi_process=True,
        encode_kwargs={"normalize_embeddings": True},
    )

    chunk_storage = initialize_storage("chunk")
    chunks = chunk_storage.get_chunks()
    faiss_cosine = FAISS.from_documents(
        chunks, embeddings, distance_strategy=DistanceStrategy.COSINE
    )
    faiss_cosine.save_local(str(output_dir))
    return None


if __name__ == "__main__":
    index_chunks()
