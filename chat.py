import streamlit as st
from rag import RagSystem
import time

class Feedback:
    def __init__(self, message_idx):
        self.message_idx = message_idx
        self.key_prefix = f"feedback_{message_idx}"

    def render(self):
        """Render feedback buttons and text input."""
        col1, col2, col3 = st.columns([1, 1, 4])

        # Thumbs up/down buttons
        with col1:
            if st.button("👍", key=f"{self.key_prefix}_up"):
                st.session_state.chat_history[self.message_idx]["feedback"] = {
                    "rating": "positive",
                    "text": st.session_state.get(f"{self.key_prefix}_text", "")
                }
                st.success("Thanks for your feedback!")

        with col2:
            if st.button("👎", key=f"{self.key_prefix}_down"):
                st.session_state.chat_history[self.message_idx]["feedback"] = {
                    "rating": "negative",
                    "text": st.session_state.get(f"{self.key_prefix}_text", "")
                }
                st.error("Thanks for your feedback!")

        # Text feedback
        with col3:
            feedback_text = st.text_input(
                "Add feedback (optional)",
                key=f"{self.key_prefix}_text",
                label_visibility="collapsed"
            )
            if feedback_text:
                if "feedback" in st.session_state.chat_history[self.message_idx]:
                    st.session_state.chat_history[self.message_idx]["feedback"]["text"] = feedback_text
                else:
                    st.session_state.chat_history[self.message_idx]["feedback"] = {
                        "rating": None,
                        "text": feedback_text
                    }

class ChatInterface:
    def __init__(self):
        self.rag_system = st.session_state.rag_system

    def _display_message(self, role, content, message_idx=None):
        """Display a chat message with appropriate styling."""
        with st.chat_message(role):
            st.markdown(content)
            if role == "assistant" and message_idx is not None:
                Feedback(message_idx).render()

    def _process_user_input(self, user_input: str) -> str:
        """Process user input and get response from RAG system."""
        try:
            with st.spinner("Thinking..."):
                response = self.rag_system.get_response(user_input)
                return response
        except Exception as e:
            st.error(f"Error getting response: {str(e)}")
            return "I apologize, but I encountered an error while processing your question. Please try again."

    def render(self):
        """Render the chat interface."""
        # Display chat history
        for i, message in enumerate(st.session_state.chat_history):
            self._display_message(
                message["role"],
                message["content"],
                i if message["role"] == "assistant" else None
            )

        # Chat input
        if user_input := st.chat_input("Ask a question about the Roman Empire"):
            # Add user message to chat
            st.session_state.chat_history.append({
                "role": "user",
                "content": user_input
            })
            self._display_message("user", user_input)

            # Get and display assistant response
            response = self._process_user_input(user_input)
            st.session_state.chat_history.append({
                "role": "assistant",
                "content": response,
                "feedback": {"rating": None, "text": ""}
            })
            self._display_message("assistant", response, len(st.session_state.chat_history) - 1)