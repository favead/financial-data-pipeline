# TO-DO:
# 1. Загрузка эмбеддингов из FAISS db
# 2. Проекция в 2d (t-sne или pca)
# 3. Визуализация, попытка отделения кластеров


from pathlib import Path


def plot_embeddings(embeddings_dir: Path) -> None:
    return None


if __name__ == "__main__":
    embeddings_dir = Path("./data/index")
    plot_embeddings(embeddings_dir)
