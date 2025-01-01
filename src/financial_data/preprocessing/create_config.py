import os
from pathlib import Path
import re
from typing import List
from prefect import flow, task
import requests


LLM_API_URL = ""
MODEL_ID = ""


FIND_FIRST_CHAPTER_PROMPT = """
"""


@flow
def create_configs() -> None:
    txt_dir = Path("./data/txt_data")
    for txt_data_dir in txt_dir.iterdir():
        for txt_filepath in txt_data_dir.iterdir():
            if txt_filepath.is_file():
                txt_headers = collect_headers(txt_filepath)
    return None


@task
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


@task
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
