from datetime import datetime
from collections import Counter
from typing import List, Dict

from langchain_core.documents import Document
from transformers import AutoTokenizer

from financial_data.utils.text_processer import TextProcesser

from ..storages import initialize_storage


def collect_eda_metrics() -> None:
    chunk_storage = initialize_storage("chunk")
    metric_storage = initialize_storage("metric")
    documents = chunk_storage.get_chunks()
    stats = collect_statistics(documents)
    for stat in stats:
        metric_storage.set_metric(stat)
    return None


def collect_statistics(
    documents: List[Document],
    model_path: str = "intfloat/multilingual-e5-small",
) -> List[Dict[str, any]]:
    tokenizer = AutoTokenizer.from_pretrained(model_path)
    text_processer = TextProcesser()
    metrics = []
    for doc in documents:
        text = doc.page_content

        tokens = tokenizer.tokenize(text)
        sentences = text.split(".")
        words = text_processer.process_text(text)
        word_frequency = Counter(words)
        most_common_words = word_frequency.most_common(5)

        metric = {
            "source_name": doc.metadata["source_name"],
            "metric_type": "eda",
            "timestamp": datetime.now(),
            "tokens": len(tokens),
            "sentences": len(sentences),
            "words": len(words),
            "most_common_words": most_common_words,
        }
        metrics.append(metric)
    return metrics
