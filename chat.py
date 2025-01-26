import streamlit as st
from rag import RagSystem
import time

class ChatInterface:
    def __init__(self):
        self.rag_system = st.session_state.rag_system

    def _display_message(self, role, content):
        """Display a chat message with appropriate styling."""
        with st.chat_message(role):
            st.markdown(content)

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
        for message in st.session_state.chat_history:
            self._display_message(
                message["role"],
                message["content"]
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
                "content": response
            })
            self._display_message("assistant", response)
