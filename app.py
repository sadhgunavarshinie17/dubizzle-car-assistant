import streamlit as st
import requests

API_URL = "http://127.0.0.1:8000"

st.set_page_config(page_title="Dubizzle Cars AI Assistant", layout="wide")

st.title("Dubizzle Cars AI Assistant")
st.caption("AI-powered car discovery, recommendations and viewing bookings")

# SESSION STATE
if "user_id" not in st.session_state:
    st.session_state.user_id = "demo_user"

if "messages" not in st.session_state:
    st.session_state.messages = []

# SIDEBAR
with st.sidebar:
    st.header("User")
    st.session_state.user_id = st.text_input("User ID", value=st.session_state.user_id)
    st.divider()
    st.markdown("### What I can do")
    st.markdown(
        """
        - Search available cars
        - Remember your preferences
        - Book vehicle viewings
        - Qualify buyer leads
        """
    )


# CHAT HISTORY
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])


# CHAT INPUT
user_message = st.chat_input("Ask me about cars at Dubizzle..")

if user_message:
    #Display user message immediately
    st.session_state.messages.append(
        {"role": "user", "content": user_message}
    )

    with st.chat_message("user"):
        st.markdown(user_message)

    # Send request to FastAPI
    try:
        response = requests.post(
            f"{API_URL}/chat",
            json = {"user_id":st.session_state.user_id, "message": user_message},
            timeout=120
        )

        response.raise_for_status()

        data = response.json()

        assistant_message = data["response"]

    except requests.exceptions.RequestException as e:
        assistant_message = (
            "Sorry, I couldn't connect to the assistant backend. "
            "Please make sure FastAPI is running."
        )

    # Display assistant response
    st.session_state.messages.append(
        {"role": "assistant", "content": assistant_message}
    )

    with st.chat_message("assistant"):
        st.markdown(assistant_message
        
        )
