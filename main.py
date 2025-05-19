from base64 import b64encode
from io import BytesIO
from uuid import uuid4

import streamlit as st

from src.models import Conversation, Message
from src.services import CrewAiService

crew_ai_service = CrewAiService()

st.session_state.setdefault("conversation", Conversation(id=str(uuid4())))

with st.sidebar:
    st.logo(
        "https://cdn.prod.website-files.com/66cf2bfc3ed15b02da0ca770/66d07240057721394308addd_Logo%20(1).svg",
        size="large",
    )
    st.title("Audio Conversation Demo")
    st.write(
        """
        This is an audio conversation demo with an AI assistant, **Erika**.

        She is a helpful Support Specialist Agent that is able to answer questions about anything that can be found on the web. Go on, try it out!

        If applications like this interest you, please find out more about us at https://crewai.com/.
        """
    )
    st.divider()
    st.link_button(
        "**Sign up for a Free Trial**", "https://app.crewai.com/", type="primary"
    )
with st.container():
    st.title("Conversation")

    conversation = st.container()

for index, message in enumerate(st.session_state.conversation.messages):
    with conversation.container():
        with st.chat_message(message.role):
            st.audio(
                message.content_bytes,
                autoplay=message.from_assistant
                and index == len(st.session_state.conversation.messages) - 1,
            )


def user_audio_created():
    audio_value = st.session_state["audio_input"]
    if audio_value:
        audio_bytes = audio_value.getvalue()
        # Create separate BytesIO objects for upload and display
        message_bytes_io = BytesIO(audio_bytes)
        user_message = Message(
            content_base64=b64encode(audio_bytes).decode(),
            content_bytes=message_bytes_io,
            role="user",
        )

        with conversation.container():
            with st.chat_message(user_message.role):
                st.audio(message_bytes_io)

            with st.spinner(text="Thinking...", show_time=True):
                process_message(user_message)


def process_message(user_message: Message):
    kickoff_response = crew_ai_service.kickoff(
        id=st.session_state.conversation.id, message=user_message
    )
    ai_message = crew_ai_service.get_ai_message(
        kickoff_response["kickoff_id"],
    )
    st.session_state.conversation.messages.append(user_message)
    st.session_state.conversation.messages.append(ai_message)


with st._bottom:
    st.audio_input(
        "Don't be shy, ask Erika anything!",
        key="audio_input",
        on_change=user_audio_created,
    )
