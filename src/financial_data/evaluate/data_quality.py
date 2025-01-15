from collections import defaultdict
from datetime import datetime
import re
from typing import Any, Dict

from ..storages import initialize_storage
from ..utils.log import get_logger


log = get_logger(__name__)


def collect_data_quality_metrics() -> None:
    """Основная функция для сбора метрик и сохранения в БД."""
    document_storage = initialize_storage("document")
    metrics_storage = initialize_storage("metric")

    try:
        documents = document_storage.get_raw_documents()
        for document in documents:
            document_text = document["content"]
            metrics = calculate_document_metrics(document_text)
            metrics["source_name"] = document["source_name"]
            metrics_storage.set_metric(metrics)

        log.info(f"Successfully processed {len(documents)} documents")
    except Exception as e:
        log.error(f"Error processing documents: {e}")
    return None


def calculate_document_metrics(content: str) -> Dict[str, Any]:
    """Расчет метрик для одного документа."""
    metrics = {
        "metric_type": "data_quality",
        "timestamp": datetime.now(),
    }

    text_metrics = analyze_text_quality(content)
    metrics.update(text_metrics)
    structure_metrics = analyze_document_structure(content)
    metrics.update(structure_metrics)

    return metrics


def analyze_text_quality(text: str) -> Dict[str, float]:
    """Анализ качества текстового содержимого."""
    metrics = {}

    # Разбиваем на строки и слова
    lines = text.split("\n")
    words = text.split()

    # Базовые метрики
    metrics["total_chars"] = len(text)
    metrics["total_words"] = len(words)
    metrics["total_lines"] = len(lines)
    metrics["non_empty_lines"] = len([line for line in lines if line.strip()])

    # Анализ слов
    avg_word_length = (
        sum(len(word) for word in words) / len(words) if words else 0
    )
    metrics["avg_word_length"] = round(avg_word_length, 2)

    # Анализ строк
    duplicate_lines = defaultdict(int)
    non_letter_lines = []
    short_lines = []
    long_lines = []

    for line in lines:
        line = line.strip()
        if line:
            # Подсчет дубликатов
            duplicate_lines[line] += 1

            # Проверка на декоративные линии
            if re.match(r"^[-_=*•·]+$", line):
                non_letter_lines.append(line)

            # Анализ длины строк
            if len(line) < 5:
                short_lines.append(line)
            elif len(line) > 200:
                long_lines.append(line)

    metrics["duplicate_lines_ratio"] = round(
        (
            len([line for line, count in duplicate_lines.items() if count > 1])
            / len(lines)
            if lines
            else 0
        ),
        3,
    )
    metrics["decorative_lines_ratio"] = round(
        len(non_letter_lines) / len(lines) if lines else 0, 3
    )
    metrics["short_lines_ratio"] = round(
        len(short_lines) / len(lines) if lines else 0, 3
    )
    metrics["long_lines_ratio"] = round(
        len(long_lines) / len(lines) if lines else 0, 3
    )

    # Анализ форматирования
    metrics["bullet_points_count"] = len(re.findall(r"[•·-]\s+\w+", text))
    metrics["numbered_lists_count"] = len(
        re.findall(r"^\d+\.\s+\w+", text, re.MULTILINE)
    )

    # Анализ пунктуации и специальных символов
    metrics["special_chars_ratio"] = round(
        (
            len(re.findall(r"[^a-zA-Zа-яА-Я0-9\s.,!?-]", text)) / len(text)
            if text
            else 0
        ),
        3,
    )

    return metrics


def analyze_document_structure(content: str) -> Dict[str, int]:
    """Анализ структуры документа."""
    # Подсчет md тегов в тексте
    metrics = {
        f"h{i}_tags_count": len(
            re.findall(r"^(?:#{i}\s)", content, re.MULTILINE)
        )
        for i in range(1, 9)  # до h8
    }

    return metrics


if __name__ == "__main__":
    collect_data_quality_metrics()
