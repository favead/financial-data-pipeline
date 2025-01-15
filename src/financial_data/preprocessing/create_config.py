import os
import re
from typing import Any, Dict, List

import requests

from ..storages import initialize_storage


LLM_API_URL = "https://api.mistral.ai/v1/chat/completions"
MODEL_ID = "mistral-7b-instruct"


DEFAULT_TINKOFF_CONFIG = {
    "remove_patterns": {
        "before_first_chapter": "#",
        "after_last_chapter": "##  Что дальше",
        "chapter_separator": "##",
    }
}


DEFAULT_BCS_CONFIG = {
    "remove_patterns": {
        "before_first_chapter": "# ",
        "after_last_chapter": "Жмите «Далее»",
        "chapter_separator": "##",
        "inline_patterns": [
            {"pattern": "Обсудить  Нравится"},
            {"pattern": "Поделиться"},
            {"pattern": "**БКС Мир инвестиций**"},
        ],
    }
}


DEFAULT_TEXTBOOK_CONFIG = {
    "remove_patterns": {
        "inline_patterns": [
            {"pattern": "Рис."},
            {"pattern": "\\[.*?\\]\\(https?:\\/\\/[^\\)]+\\)"},
            {"pattern": "-+"},
            {"pattern": "http"},
            {"pattern": "\\*\\*FIGURE \\d+\\.\\d+"},
            {"pattern": "_Рис"},
            {"pattern": "_Figure"},
            {"pattern": "_Source"},
            {"pattern": "-+"},
            {"pattern": "www."},
            {"pattern": "EP-CM&SL"},
        ],
    }
}


def create_configs() -> None:
    document_storage = initialize_storage("document")
    config_storage = initialize_storage("config")
    raw_documents = document_storage.get_raw_documents()
    source_names = set(
        [raw_document["source_name"] for raw_document in raw_documents]
    )
    for source_name in source_names:
        if source_name == "tinkoff":
            config = DEFAULT_TINKOFF_CONFIG
        elif source_name == "bcs":
            config = DEFAULT_BCS_CONFIG
        else:
            config = DEFAULT_TEXTBOOK_CONFIG
        config_storage.set_config(source_name, config)
    return None


def get_remove_patterns_by_document(raw_document: str) -> Dict[str, Any]:
    """
    Функция для наполнения конфигурационного файла для очистки документа
    от нерелевантной информации.

    Пока что не реализовано.
    """
    return {}


def generate(
    prompt: str,
    max_new_tokens: int = 2048,
    temperature: float = 0.7,
    random_seed: int = 42,
) -> str:
    messages = [{"role": "user", "content": prompt}]
    response = requests.post(
        LLM_API_URL,
        json={
            "model": MODEL_ID,
            "messages": messages,
            "max_tokens": max_new_tokens,
            "temperature": temperature,
            "random_seed": random_seed,
        },
        headers={"Authorization": f"Bearer {os.getenv("MISTRAL_API_KEY")}"},
    )
    try:
        model_output = response.json()["choices"][0]["message"]["content"]
    except KeyError:
        model_output = ""
    return model_output


def collect_headers(txt_path: str) -> List[str]:
    pattern = re.Pattern("")
    headers = []
    with open(txt_path, "r") as f:
        for line in f.readline():
            if pattern.match(line):
                headers.append(line)
    return headers


if __name__ == "__main__":
    create_configs()
