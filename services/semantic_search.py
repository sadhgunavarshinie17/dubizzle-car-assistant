from pathlib import Path

import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

from services.inventory import load_inventory


MODEL_NAME = "all-MiniLM-L6-v2"
EMBEDDINGS_PATH = Path("data/car_embeddings.npy")

model = SentenceTransformer(MODEL_NAME)


def build_search_text(row):
    return (
        f"{row['year']} {row['make']} {row['model']} {row['trim']} "
        f"{row['title']} {row['description']}"
    )


def load_embeddings(df):
    if EMBEDDINGS_PATH.exists():
        return np.load(EMBEDDINGS_PATH)

    documents = df["search_text"].tolist()
    embeddings = model.encode(documents)

    EMBEDDINGS_PATH.parent.mkdir(parents=True, exist_ok=True)
    np.save(EMBEDDINGS_PATH, embeddings)

    return embeddings


def semantic_search(query, top_k=5):
    df = load_inventory().copy()

    df["search_text"] = df.apply(build_search_text, axis=1)

    document_embeddings = load_embeddings(df)

    query_embedding = model.encode([query])

    scores = cosine_similarity(
        query_embedding,
        document_embeddings
    )[0]

    df["score"] = scores

    return df.sort_values("score", ascending=False).head(top_k)