import os
from functools import lru_cache

os.environ.setdefault("TOKENIZERS_PARALLELISM", "false")
os.environ.setdefault("HF_HUB_DISABLE_TELEMETRY", "1")

import config


@lru_cache(maxsize=1)
def get_embedding_model():
    from sentence_transformers import SentenceTransformer

    return SentenceTransformer(config.EMBEDDING_MODEL)


def embed_texts(texts: list[str]) -> list[list[float]]:
    if not texts:
        return []
    model = get_embedding_model()
    vectors = model.encode(texts, normalize_embeddings=True, show_progress_bar=False)
    return [v.tolist() for v in vectors]


def embed_query(query: str) -> list[float]:
    return embed_texts([query])[0]
