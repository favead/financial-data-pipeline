from pathlib import Path
import matplotlib.pyplot as plt
from collections import Counter
from typing import Any, List, Dict

from langchain_core.documents import Document
import pandas as pd
from transformers import AutoTokenizer

from ..utils.jsonl import (
    load_documents_from_jsonl,
)
from ..utils.text_processer import TextProcesser


def collect_statistics(
    documents: List[Document],
    model_path: str = "intfloat/multilingual-e5-small",
) -> Dict[str, any]:
    tokenizer = AutoTokenizer.from_pretrained(model_path)
    total_documents = len(documents)
    total_tokens = 0
    total_sentences = 0
    metadata_counter = Counter()
    tokens_per_document = []
    tokens_per_source = {}
    sentences_per_document = []

    for doc in documents:
        text = doc.page_content
        tokens = tokenizer.tokenize(text)
        tokens_per_document.append(len(tokens))
        total_tokens += len(tokens)

        try:
            tokens_per_source[doc.metadata["source"]] += [len(tokens)]
        except KeyError:
            tokens_per_source[doc.metadata["source"]] = [len(tokens)]

        sentences = text.split(".")
        sentences_per_document.append(len(sentences))
        total_sentences += len(sentences)

        for key, value in doc.metadata.items():
            metadata_counter[key] += 1

    mean_tokens_per_source = {
        k: sum(v) / len(v) for k, v in tokens_per_source.items()
    }
    sum_tokens_per_source = {k: sum(v) for k, v in tokens_per_source.items()}

    return {
        "total_documents": total_documents,
        "total_tokens": total_tokens,
        "total_sentences": total_sentences,
        "metadata_aggregation": metadata_counter,
        "tokens_per_document": tokens_per_document,
        "sentences_per_document": sentences_per_document,
        "tokens_per_source": sum_tokens_per_source,
        "mean_tokens_per_source": mean_tokens_per_source,
    }


def perform_words_count(
    documents: List[Document], text_processer: TextProcesser
) -> Counter:
    entities_counter = Counter()

    for doc in documents:
        text = doc.page_content
        words = text_processer.process_text(text)
        for ent in words:
            entities_counter[ent] += 1

    return entities_counter


def process_documents_in_directory(directory: Path) -> None:
    jsonl_files = [f for f in directory.glob("*.jsonl")]
    all_documents = []

    for jsonl_file in jsonl_files:
        documents = load_documents_from_jsonl(jsonl_file)
        all_documents.extend(documents)

    stats = collect_statistics(all_documents)
    text_processer = TextProcesser()
    common_words = perform_words_count(all_documents, text_processer)
    plot_statistics(stats, common_words=common_words)
    return None


def plot_statistics(
    stats: Dict[str, Any], common_words: Counter | None = None
) -> None:
    total_documents = stats["total_documents"]
    total_tokens = stats["total_tokens"]
    total_sentences = stats["total_sentences"]

    df = {
        "Total Documents": [total_documents],
        "Total Tokens": [total_tokens],
        "Total Sentences": [total_sentences],
    }
    comb_stat = pd.DataFrame.from_dict(df)
    comb_stat.to_csv("./artifacts/combined_statistics.csv", index=False)

    fig, ax = plt.subplots(figsize=(8, 5))
    ax.bar(range(total_documents), stats["tokens_per_document"])
    ax.set_title("Tokens per Document")
    ax.set_xlabel("Document")
    ax.set_ylabel("Tokens")
    plt.xticks(rotation=90)
    plt.tight_layout()
    plt.savefig("./artifacts/tokens_per_document.png")

    fig, ax = plt.subplots(figsize=(8, 5))
    ax.bar(range(total_documents), stats["sentences_per_document"])
    ax.set_title("Sentences per Document")
    ax.set_xlabel("Document")
    ax.set_ylabel("Sentences")
    plt.xticks(rotation=90)
    plt.tight_layout()
    plt.savefig("./artifacts/sentences_per_document.png")

    fig, ax = plt.subplots(figsize=(8, 5))
    metadata = stats["metadata_aggregation"]
    ax.bar(metadata.keys(), metadata.values())
    ax.set_title("Metadata Aggregation")
    ax.set_xlabel("Metadata Key")
    ax.set_ylabel("Frequency")
    plt.xticks(rotation=90)
    plt.tight_layout()
    plt.savefig("./artifacts/metadata_aggregation.png")

    _, ax = plt.subplots(figsize=(8, 5))
    tokens_per_source = stats["tokens_per_source"]
    ax.bar(tokens_per_source.keys(), tokens_per_source.values())
    ax.set_title("Tokens per source")
    ax.set_xlabel("Source name")
    ax.set_ylabel("Tokens")
    plt.xticks(rotation=90)
    plt.tight_layout()
    plt.savefig("./artifacts/tokens_per_source.png")

    _, ax = plt.subplots(figsize=(8, 5))
    tokens_per_source = stats["mean_tokens_per_source"]
    ax.bar(tokens_per_source.keys(), tokens_per_source.values())
    ax.set_title("Mean tokens per source")
    ax.set_xlabel("Source name")
    ax.set_ylabel("Tokens")
    plt.xticks(rotation=90)
    plt.tight_layout()
    plt.savefig("./artifacts/mean_tokens_per_source.png")

    if common_words:
        top_entities = common_words.most_common(50)
        labels, counts = zip(*top_entities)

        fig, ax = plt.subplots(figsize=(10, 6))
        ax.bar(labels, counts)
        ax.set_title("Top 50 Word Frequency")
        ax.set_xlabel("Entity")
        ax.set_ylabel("Frequency")
        plt.xticks(rotation=90)
        plt.tight_layout()
        plt.savefig("./artifacts/top_common_words.png")

    return None


if __name__ == "__main__":
    data_dir = Path("./data/chunks")
    process_documents_in_directory(data_dir)
