from pathlib import Path
import matplotlib.pyplot as plt
from collections import Counter
from typing import Any, List, Dict

import langdetect
from langchain_core.documents import Document
import pandas as pd
from transformers import pipeline, AutoTokenizer

from ..utils.jsonl import (
    load_documents_from_jsonl,
)

ner_en = pipeline(
    "ner", model="dbmdz/bert-large-cased-finetuned-conll03-english"
)
ner_ru = pipeline("ner", model="Gherman/bert-base-NER-Russian")


def detect_language(text: str) -> str:
    try:
        lang = langdetect.detect(text)
        return lang
    except Exception:
        return "unknown"


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
    sentences_per_document = []

    for doc in documents:
        text = doc.page_content
        tokens = tokenizer.tokenize(text)
        tokens_per_document.append(len(tokens))
        total_tokens += len(tokens)

        sentences = text.split(".")
        sentences_per_document.append(len(sentences))
        total_sentences += len(sentences)

        for key, value in doc.metadata.items():
            metadata_counter[key] += 1

    return {
        "total_documents": total_documents,
        "total_tokens": total_tokens,
        "total_sentences": total_sentences,
        "metadata_aggregation": metadata_counter,
        "tokens_per_document": tokens_per_document,
        "sentences_per_document": sentences_per_document,
    }


def perform_ner(documents: List[Document]) -> Counter:
    entities_counter = Counter()

    for doc in documents:
        text = doc.page_content
        lang = detect_language(text)

        if lang == "en":
            ner_results = ner_en(text)
        elif lang == "ru":
            ner_results = ner_ru(text)
        else:
            continue

        for ent in ner_results:
            entities_counter[ent["word"]] += 1

    return entities_counter


def process_documents_in_directory(directory: Path):
    jsonl_files = [f for f in directory.glob("*.jsonl")]
    all_documents = []

    for jsonl_file in jsonl_files:
        documents = load_documents_from_jsonl(jsonl_file)
        all_documents.extend(documents)

    stats = collect_statistics(all_documents)
    entities = perform_ner(all_documents)
    plot_statistics(stats, entities)


def plot_statistics(stats: Dict[str, Any], entities: Counter):
    total_documents = stats["total_documents"]
    total_tokens = stats["total_tokens"]
    total_sentences = stats["total_sentences"]

    df = {
        "Total Documents": [total_documents],
        "Total Tokens": [total_tokens],
        "Total Sentences": [total_sentences],
    }
    comb_stat = pd.DataFrame.from_dict(df)
    comb_stat.to_csv("./data/artifacts/combined_statistics.csv", index=False)

    fig, ax = plt.subplots(figsize=(6, 4))
    ax.bar(range(total_documents), stats["tokens_per_document"])
    ax.set_title("Tokens per Document")
    ax.set_xlabel("Document")
    ax.set_ylabel("Tokens")
    plt.tight_layout()
    plt.savefig("./data/artifacts/tokens_per_document.png")

    fig, ax = plt.subplots(figsize=(6, 4))
    ax.bar(range(total_documents), stats["sentences_per_document"])
    ax.set_title("Sentences per Document")
    ax.set_xlabel("Document")
    ax.set_ylabel("Sentences")
    plt.tight_layout()
    plt.savefig("./data/artifacts/sentences_per_document.png")

    fig, ax = plt.subplots(figsize=(6, 4))
    metadata = stats["metadata_aggregation"]
    ax.bar(metadata.keys(), metadata.values())
    ax.set_title("Metadata Aggregation")
    ax.set_xlabel("Metadata Key")
    ax.set_ylabel("Frequency")
    plt.tight_layout()
    plt.savefig("./data/artifacts/metadata_aggregation.png")

    top_entities = entities.most_common(50)
    labels, counts = zip(*top_entities)

    fig, ax = plt.subplots(figsize=(10, 6))
    ax.bar(labels, counts)
    ax.set_title("Top 50 NER Entity Frequency")
    ax.set_xlabel("Entity")
    ax.set_ylabel("Frequency")
    plt.tight_layout()
    plt.savefig("./data/artifacts/top_ner_entities.png")

    return None


if __name__ == "__main__":
    data_dir = Path("./data/chunks")
    process_documents_in_directory(data_dir)
