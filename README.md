# dubizzle Cars AI Assistant

An AI-powered car shopping assistant built as a technical case study for dubizzle Cars.

The assistant can search the available vehicle inventory, remember user preferences across conversations, qualify potential buyers, save leads, and simulate vehicle viewing bookings.

> This is an independent prototype developed as part of a technical case study. It is not an official dubizzle product.

## Features

- Natural-language car search
- Hybrid semantic + structured inventory retrieval
- Multi-turn conversation context
- Long-term user preference memory
- Lead qualification and CSV storage
- Vehicle viewing booking
- Automotive-only guardrails
- FastAPI backend with Streamlit interface

## Project Structure

```text
dubizzle-car-assistant/
│
├── data/
│   ├── cars.xlsx
│   └── ...
│
├── services/
│   ├── inventory.py
│   ├── semantic_search.py
│   ├── memory.py
│   ├── booking.py
│   └── leads.py
│
├── assets/
│   └── logo.png
│
├── app.py
├── main.py
├── pyproject.toml
├── uv.lock
├── .env.example
└── README.md
````

## Setup

### 1. Install dependencies

This project uses `uv` for dependency management.

```bash
uv sync
```

### 2. Configure the Gemini API key

Create a `.env` file in the project root:

```text
GEMINI_API_KEY=your_gemini_api_key_here
```

### 3. Start the FastAPI backend

```bash
uv run uvicorn main:app --reload
```

The API will run at:

```text
http://127.0.0.1:8000
```

### 4. Start the Streamlit interface

In a second terminal:

```bash
uv run streamlit run app.py
```

The interface will be available at:

```text
http://localhost:8501
```

## Architecture

The Streamlit client communicates with the FastAPI backend through the `/chat` endpoint.

Gemini is used as the conversational layer and can call tools for inventory search, preference storage, lead saving, and viewing bookings.

Inventory retrieval uses a hybrid approach. Structured filters such as make, model, and year are applied first, followed by semantic similarity search using sentence embeddings. This allows both explicit searches such as "2014 Ford Explorer" and more natural requirements to retrieve relevant listings from the available inventory.

SQLite is used for conversation history and long-term user preferences. This keeps the implementation local and simple while demonstrating both short-term conversational context and persistence across separate sessions. Qualified leads are stored in a local CSV file, while viewing appointments are stored in SQLite.

## Design Decisions

The system separates the conversational agent from the application logic. Gemini decides when a tool is required, while inventory retrieval, memory, lead storage, and booking are handled by deterministic Python services. This keeps vehicle information grounded in the provided inventory rather than relying on generated information.

The prototype focuses on the main car-shopping workflow rather than production infrastructure. It uses local SQLite/CSV storage, a local inventory file, simulated viewing availability, and a Streamlit interface. These choices keep the prototype easy to run and demonstrate the required architecture without adding unnecessary infrastructure.

## Out of Scope

The following are intentionally outside the scope of this prototype:

* Real payment processing
* Real dealership/calendar integration
* Production authentication and user accounts
* Real-time vehicle inventory synchronization
* Production database deployment
* Actual booking confirmations
* Competitor marketplace integration

## Example Conversations

### Multi-turn inventory search

```text
User: I'm looking for a Ford Explorer.

Assistant: [Returns matching Ford Explorer listings]

User: Only show me ones from 2014 or newer.

Assistant: [Narrows the results]

User: What was the car you found for me?

Assistant: [Recalls the vehicle from the conversation]
```

### Long-term memory

A user can provide preferences in one conversation and return using the same user ID in a completely new session. Stored preferences can then be used to personalise future car searches.

### Viewing booking

```text
User: I'd like to book a viewing for listing 53 on September 12 at 3 PM.
      My name is Alex and my contact is 0500000000.

Assistant: [Validates the listing and booking slot, then creates the booking]
```

## Technologies

* Python
* FastAPI
* Streamlit
* Google Gemini
* Sentence Transformers
* scikit-learn
* Pandas
* SQLite
* uv
