from services.semantic_search import semantic_search

results = semantic_search(
    "SUV with warranty and low mileage",
    top_k=5
)

print(results[
    ["Listing_ID", "year", "make", "model", "trim", "score"]
])