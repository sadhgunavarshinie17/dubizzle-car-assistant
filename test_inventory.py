from services.semantic_search import hybrid_search


results = hybrid_search(
    query="Ford Explorer",
    make="ford",
    model_name="explorer",
    min_year=2014,
    top_k=5
)

print(
    results[
        ["Listing_ID", "year", "make", "model", "trim", "score"]
    ]
)