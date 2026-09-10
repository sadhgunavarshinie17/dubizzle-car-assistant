import os
import json

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from google import genai

from services.inventory import load_inventory
from services.semantic_search import hybrid_search
from services.memory import (
    initialize_memory,
    save_message,
    get_recent_messages,
    save_preferences,
    get_preferences
)
from services.booking import initialize_bookings, book_viewing
from services.leads import save_lead

initialize_bookings()

load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

app = FastAPI(
    title="dubizzle Cars AI Assistant",
    description="AI assistant backend for exploring car inventory",
    version="1.0.0"
)

initialize_memory()


class SearchRequest(BaseModel):
    query: str
    make: str | None = None
    model: str | None = None
    min_year: int | None = None
    max_year: int | None = None
    top_k: int = 5


class ChatRequest(BaseModel):
    user_id: str
    message: str


@app.get("/")
def root():
    return {"message": "dubizzle Cars AI Assistant API is running"}


@app.get("/inventory")
def get_inventory():
    df = load_inventory()
    return df.to_dict(orient="records")


@app.post("/search")
def search_cars(request: SearchRequest):
    results = hybrid_search(
        query=request.query,
        make=request.make,
        model_name=request.model,
        min_year=request.min_year,
        max_year=request.max_year,
        top_k=request.top_k
    )

    return {
        "query": request.query,
        "count": len(results),
        "results": results.to_dict(orient="records")
    }


search_inventory_tool = {
    "type": "function",
    "name": "search_inventory",
    "description": "Search the dubizzle car inventory for vehicles matching the user's requirements.",
    "parameters": {
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "The user's natural-language car search query."
            },
            "make": {
                "type": "string",
                "description": "Car manufacturer, if specified."
            },
            "model": {
                "type": "string",
                "description": "Car model, if specified."
            },
            "min_year": {
                "type": "integer",
                "description": "Minimum acceptable vehicle year, if specified."
            },
            "max_year": {
                "type": "integer",
                "description": "Maximum acceptable vehicle year, if specified."
            },
            "top_k": {
                "type": "integer",
                "description": "Maximum number of cars to return."
            }
        },
        "required": ["query"]
    }
}


save_preferences_tool = {
    "type": "function",
    "name": "save_preferences",
    "description": "Save useful car preferences that the user explicitly provides for future conversations.",
    "parameters": {
        "type": "object",
        "properties": {
            "name": {
                "type": "string",
                "description": "The user's name, if provided."
            },
            "preferred_make": {
                "type": "string",
                "description": "The user's preferred car make."
            },
            "preferred_model": {
                "type": "string",
                "description": "The user's preferred car model."
            },
            "min_year": {
                "type": "integer",
                "description": "The minimum vehicle year the user wants."
            },
            "max_year": {
                "type": "integer",
                "description": "The maximum vehicle year the user wants."
            },
            "budget": {
                "type": "number",
                "description": "The user's approximate maximum budget."
            }
        }
    }
}


book_viewing_tool = {
    "type": "function",
    "name": "book_viewing",
    "description": "Book a car viewing appointment for a vehicle in the dubizzle inventory.",
    "parameters": {
        "type": "object",
        "properties": {
            "listing_id": {
                "type": "integer",
                "description": "The Listing_ID of the car the user wants to view."
            },
            "booking_date": {
                "type": "string",
                "description": "Viewing date in YYYY-MM-DD format."
            },
            "booking_time": {
                "type": "string",
                "description": "Viewing time in HH:MM 24-hour format."
            },
            "name": {
                "type": "string",
                "description": "Customer's name."
            },
            "contact": {
                "type": "string",
                "description": "Customer's phone number or contact information."
            }
        },
        "required": [
            "listing_id",
            "booking_date",
            "booking_time",
            "name",
            "contact"
        ]
    }
}


save_lead_tool = {
    "type": "function",
    "name": "save_lead",
    "description": "Save a qualified car buyer lead after the user has provided their contact details and purchase information.",
    "parameters": {
        "type": "object",
        "properties": {
            "name": {
                "type": "string",
                "description": "Customer's name."
            },
            "contact": {
                "type": "string",
                "description": "Customer's phone number or contact information."
            },
            "listing_id": {
                "type": "integer",
                "description": "Listing ID of the car the customer is interested in."
            },
            "budget": {
                "type": "number",
                "description": "Customer's approximate budget in AED."
            },
            "timeline": {
                "type": "string",
                "description": "When the customer plans to purchase, such as immediately, within 1 month, or within 3 months."
            },
            "wants_viewing": {
                "type": "boolean",
                "description": "Whether the customer wants to book a viewing."
            }
        },
        "required": [
            "name",
            "contact"
        ]
    }
}




SYSTEM_PROMPT = """
You are a car shopping assistant for dubizzle.
Your job is to help users explore the available car inventory, understand their preferences, and eventually book vehicle viewings.

Rules:

1. Only provide factual information about vehicles when it comes from the inventory search results or information provided by the user.

2. When the user asks about available cars, use the search_inventory tool instead of making up vehicles, prices, specifications, or listings.

3. If the user's request is vague, ask a short follow-up question to understand what kind of car they want.

4. You can have normal casual conversations with the user.

5. If the user asks about topics unrelated to cars, politely explain that you can only help with car-related requests.

6. Do not recommend competitor car marketplaces or redirect users to competing platforms.

7. Never invent a listing if no matching vehicle exists in the inventory.

8. If no matching cars are found, clearly tell the user that there are currently no matching vehicles in the available inventory.

9. Keep responses concise and helpful.

10. When presenting cars, mention useful information such as: listing ID, year, make, model, trim, title, and relevant details from the listing.

11. Use stored user preferences when they are relevant to the user's current request.

12. Do not claim that you remember something unless it is present in the conversation history or stored preferences.

13. When a user shows clear buying intent, qualify the lead by collecting their name and contact information. If available, also capture their interested listing, approximate budget, and purchase timeline.

14. Do not invent missing lead information. Ask the user for information that is required before saving a qualified lead.

15. A viewing can only be booked when the user has provided:
    - listing ID
    - name
    - contact
    - viewing date
    - viewing time

16. Before booking a viewing, use the book_viewing tool. Do not claim that a viewing has been booked unless the tool returns success.

17. When a user provides enough information to qualify them, use the save_lead tool to store the lead.

18. If the user wants a viewing but has not provided a date or time, ask for their preferred date and time. Viewing availability is Monday to Saturday, 8:00 AM to 8:00 PM.

19. If a booking attempt fails because the slot is unavailable or invalid, clearly explain the reason and ask the user for another suitable slot.

20. Never claim that a lead was saved unless the save_lead tool succeeds.
"""


@app.post("/chat")
def chat(request: ChatRequest):
    history = get_recent_messages(request.user_id)
    preferences = get_preferences(request.user_id)

    cars = []

    conversation = "\n".join(
        f"{role}: {message}"
        for role, message in history
    )

    conversation += f"\nuser: {request.message}"

    if preferences:
        conversation = (
            f"User preferences from previous conversations:\n"
            f"{json.dumps(preferences)}\n\n"
            f"Conversation:\n"
            f"{conversation}"
        )

    try:
        interaction = client.interactions.create(
            model="gemini-3.6-flash",
            input=conversation,
            system_instruction=SYSTEM_PROMPT,
            tools=[search_inventory_tool, save_preferences_tool, book_viewing_tool, save_lead_tool]
        )

    except Exception as error:
        if "429" in str(error):
            raise HTTPException(
                status_code=429,
                detail="Gemini API quota exceeded. Please try again shortly."
            )

        raise HTTPException(
            status_code=500,
            detail="Something went wrong while contacting the AI assistant."
        )
    

    for step in interaction.steps:
        if step.type == "function_call":
            arguments = step.arguments

            if step.name == "search_inventory":
                results = hybrid_search(
                    query=arguments["query"],
                    make=arguments.get("make"),
                    model_name=arguments.get("model"),
                    min_year=arguments.get("min_year"),
                    max_year=arguments.get("max_year"),
                    top_k=arguments.get("top_k", 5)
                )

                cars = results[
                    [
                        "Listing_ID",
                        "year",
                        "make",
                        "model",
                        "trim",
                        "title",
                        "description"
                    ]
                ].fillna("").to_dict(orient="records")

                result = cars

            elif step.name == "save_preferences":
                save_preferences(
                    user_id=request.user_id,
                    name=arguments.get("name"),
                    preferred_make=arguments.get("preferred_make"),
                    preferred_model=arguments.get("preferred_model"),
                    min_year=arguments.get("min_year"),
                    max_year=arguments.get("max_year"),
                    budget=arguments.get("budget")
                )

                result = {"status": "Preferences saved successfully."}

            elif step.name == "book_viewing":
                result = book_viewing(
                    user_id=request.user_id,
                    listing_id=arguments.get("listing_id"),
                    booking_date=arguments.get("booking_date"),
                    booking_time=arguments.get("booking_time"),
                    name=arguments.get("name"),
                    contact=arguments.get("contact")
                )

            elif step.name == "save_lead":
                result = save_lead(
                    user_id=request.user_id,
                    name=arguments.get("name"),
                    contact=arguments.get("contact"),
                    listing_id=arguments.get("listing_id"),
                    budget=arguments.get("budget"),
                    timeline=arguments.get("timeline"),
                    wants_viewing=arguments.get("wants_viewing", False)
                )

            final_interaction = client.interactions.create(
                model="gemini-3.6-flash",
                system_instruction=SYSTEM_PROMPT,
                previous_interaction_id=interaction.id,
                tools=[search_inventory_tool, save_preferences_tool, book_viewing_tool, save_lead_tool],
                input=[
                    {
                        "type": "function_result",
                        "name": step.name,
                        "call_id": step.id,
                        "result": [
                            {
                                "type": "text",
                                "text": json.dumps(result)
                            }
                        ]
                    }
                ]
            )

            save_message(request.user_id, "user", request.message)
            save_message(request.user_id, "assistant", final_interaction.output_text)
            return {"response": final_interaction.output_text, "cars": cars}

    response_text = interaction.output_text

    if not response_text:
        response_text = "I found the relevant information, but I couldn't generate a response. Please try again."

    save_message(request.user_id, "user", request.message)
    save_message(request.user_id, "assistant", response_text)

    return {
        "response": response_text,
        "cars": cars
    }