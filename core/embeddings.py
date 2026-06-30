import os
from functools import lru_cache

os.environ.setdefault("TOKENIZERS_PARALLELISM", "false")
os.environ.setdefault("HF_HUB_DISABLE_TELEMETRY", "1")

import config


@lru_cache(maxsize=1)
def get_embedding_model():
    from fastembed import TextEmbedding

    return TextEmbedding(model_name=config.EMBEDDING_MODEL)


def embed_texts(texts: list[str]) -> list[list[float]]:
    if not texts:
        return []
    model = get_embedding_model()
    return [vec.tolist() for vec in model.embed(texts)]


def embed_query(query: str) -> list[float]:
    return embed_texts([query])[0]
