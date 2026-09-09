import streamlit as st
import requests


API_URL = "http://127.0.0.1:8000"


# --------------------------------------------------
# Page configuration
# --------------------------------------------------

st.set_page_config(
    page_title="dubizzle Cars",
    page_icon="directions_car",
    layout="wide"
)


# --------------------------------------------------
# Custom styling
# --------------------------------------------------

st.markdown(
    """
    <style>

    .block-container {
        max-width: 1100px;
        padding-top: 2.5rem;
        padding-bottom: 3rem;
    }

    .app-header {
        margin-bottom: 2rem;
    }

    .app-title {
        font-size: 2rem;
        font-weight: 650;
        letter-spacing: -0.5px;
        margin-bottom: 0.25rem;
    }

    .app-subtitle {
        color: #6b7280;
        font-size: 0.95rem;
    }

    section[data-testid="stSidebar"] {
        border-right: 1px solid #e5e7eb;
    }

    .sidebar-section {
        margin-top: 1.5rem;
        margin-bottom: 0.75rem;
        font-size: 0.78rem;
        font-weight: 600;
        color: #6b7280;
        text-transform: uppercase;
        letter-spacing: 0.6px;
    }

    .capability {
        padding: 0.75rem 0;
        border-bottom: 1px solid #f0f0f0;
    }

    .capability:last-child {
        border-bottom: none;
    }

    .capability-title {
        font-size: 0.9rem;
        font-weight: 600;
        color: #374151;
        margin-bottom: 0.15rem;
    }

    .capability-description {
        font-size: 0.8rem;
        line-height: 1.4;
        color: #6b7280;
    }

    [data-testid="stChatMessage"] {
        padding-top: 0.75rem;
        padding-bottom: 0.75rem;
    }

    .results-heading {
        font-size: 0.95rem;
        font-weight: 600;
        color: #374151;
        margin-top: 1rem;
        margin-bottom: 0.5rem;
    }

    .car-card {
        border: 1px solid #e5e7eb;
        border-radius: 12px;
        padding: 1rem 1.1rem;
        margin: 0.6rem 0;
        background: white;
    }

    .car-title {
        font-size: 1.05rem;
        font-weight: 650;
        color: #111827;
        margin-bottom: 0.2rem;
    }

    .car-meta {
        color: #6b7280;
        font-size: 0.85rem;
        margin-bottom: 0.55rem;
    }

    .car-description {
        color: #374151;
        font-size: 0.88rem;
        line-height: 1.5;
    }

    .listing-id {
        display: inline-block;
        background: #f3f4f6;
        border-radius: 6px;
        padding: 0.2rem 0.45rem;
        font-size: 0.72rem;
        color: #4b5563;
        margin-top: 0.6rem;
    }

    [data-testid="stChatInput"] {
        margin-top: 1rem;
    }

    </style>
    """,
    unsafe_allow_html=True
)


# --------------------------------------------------
# Session state
# --------------------------------------------------

if "user_id" not in st.session_state:
    st.session_state.user_id = "demo_user"

if "messages" not in st.session_state:
    st.session_state.messages = []


# --------------------------------------------------
# Header
# --------------------------------------------------

st.image(
    "assets/logo.png",
    width=180
)

st.markdown(
    '<div class="app-title">dubizzle Cars</div>',
    unsafe_allow_html=True
)

st.caption(
    "Find the right car from our available inventory"
)


# --------------------------------------------------
# Sidebar
# --------------------------------------------------

with st.sidebar:

    st.markdown(
        '<div class="sidebar-section">User</div>',
        unsafe_allow_html=True
    )

    st.session_state.user_id = st.text_input(
        "User ID",
        value=st.session_state.user_id,
        label_visibility="collapsed"
    )

    st.divider()

    st.markdown(
        '<div class="sidebar-section">Assistant</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        """
        <div class="capability">
            <div class="capability-title">
                Car discovery
            </div>
            <div class="capability-description">
                Search and compare vehicles from the available inventory.
            </div>
        </div>

        <div class="capability">
            <div class="capability-title">
                Personalised search
            </div>
            <div class="capability-description">
                Your preferences can be remembered across conversations.
            </div>
        </div>

        <div class="capability">
            <div class="capability-title">
                Viewing appointments
            </div>
            <div class="capability-description">
                Find a suitable time and book a vehicle viewing.
            </div>
        </div>

        <div class="capability">
            <div class="capability-title">
                Buyer enquiries
            </div>
            <div class="capability-description">
                Share your requirements and we'll record your enquiry.
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.divider()

    st.caption("dubizzle Cars AI Assistant")


# --------------------------------------------------
# Chat history
# --------------------------------------------------

for message in st.session_state.messages:

    with st.chat_message(message["role"]):

        st.markdown(message["content"])



# --------------------------------------------------
# Chat input
# --------------------------------------------------

user_message = st.chat_input(
    "Ask about available cars..."
)


if user_message:

    st.session_state.messages.append(
        {
            "role": "user",
            "content": user_message
        }
    )

    with st.chat_message("user"):
        st.markdown(user_message)


    retrieved_cars = []

    response = None

    try:

        response = requests.post(
            f"{API_URL}/chat",
            json={
                "user_id": st.session_state.user_id,
                "message": user_message
            },
            timeout=120
        )

        response.raise_for_status()

        data = response.json()

        assistant_message = data["response"]
        retrieved_cars = data.get("cars", [])


    except requests.exceptions.RequestException as error:

        if response is not None and response.status_code == 429:
            assistant_message = (
                "The assistant has temporarily reached its API limit. "
                "Please try again shortly."
            )
        else:
            assistant_message = (
                "I couldn't connect to the assistant right now. "
                "Please make sure the FastAPI server is running."
            )


    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": assistant_message,
            "cars": retrieved_cars
        }
    )


    with st.chat_message("assistant"):
        st.markdown(assistant_message)

