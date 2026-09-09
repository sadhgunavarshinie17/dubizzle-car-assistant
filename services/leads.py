import csv
from pathlib import Path

LEADS_PATH = Path("data/leads.csv")


def save_lead(user_id, name, contact, listing_id=None, budget=None, timeline=None, wants_viewing=False):
    LEADS_PATH.parent.mkdir(parents=True, exist_ok=True)

    file_exists = LEADS_PATH.exists()

    with open(LEADS_PATH, "a", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=["user_id", "name", "contact", "listing_id", "budget", "timeline", "wants_viewing"])

        if not file_exists:
            writer.writeheader()

        writer.writerow({
            "user_id": user_id,
            "name": name,
            "contact": contact,
            "listing_id": listing_id,
            "budget": budget,
            "timeline": timeline,
            "wants_viewing": wants_viewing
        })

    return {
        "success": True,
        "message": "Lead saved successfully."
    }