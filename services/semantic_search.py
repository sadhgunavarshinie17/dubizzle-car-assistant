from pathlib import Path

import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

from services.inventory import load_inventory


MODEL_NAME = "all-MiniLM-L6-v2"
EMBEDDINGS_PATH = Path("data/car_embeddings.npy")

model = SentenceTransformer(MODEL_NAME)


def build_search_text(row):
    return f"{row['year']} {row['make']} {row['model']} {row['trim']} {row['title']} {row['description']}"


def load_embeddings(df):
    if EMBEDDINGS_PATH.exists():
        return np.load(EMBEDDINGS_PATH)

    documents = df["search_text"].tolist()
    embeddings = model.encode(documents)

    EMBEDDINGS_PATH.parent.mkdir(parents=True, exist_ok=True)
    np.save(EMBEDDINGS_PATH, embeddings)

    return embeddings


def semantic_search(query, df, top_k=5):
    df = df.copy()
    df["search_text"] = df.apply(build_search_text, axis=1)

    document_embeddings = load_embeddings(df)
    query_embedding = model.encode([query])

    scores = cosine_similarity(query_embedding, document_embeddings)[0]
    df["score"] = scores

    return df.sort_values("score", ascending=False).head(top_k)


def hybrid_search(
    query,
    make=None,
    model_name=None,
    min_year=None,
    max_year=None,
    top_k=5
):
    df = load_inventory().copy()

    if make:
        df = df[df["make"].str.lower() == make.lower()]

    if model_name:
        df = df[df["model"].str.lower() == model_name.lower()]

    if min_year:
        df = df[df["year"] >= min_year]

    if max_year:
        df = df[df["year"] <= max_year]

    if df.empty:
        return df

    full_inventory = load_inventory().copy()
    full_inventory["search_text"] = full_inventory.apply(build_search_text, axis=1)

    document_embeddings = load_embeddings(full_inventory)
    query_embedding = model.encode([query])

    scores = cosine_similarity(query_embedding, document_embeddings)[0]
    full_inventory["score"] = scores

    filtered_ids = set(df["Listing_ID"])
    results = full_inventory[full_inventory["Listing_ID"].isin(filtered_ids)]

    return results.sort_values("score", ascending=False).head(top_k)