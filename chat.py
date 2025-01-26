import streamlit as st
from rag import RagSystem
import time
import httpx
from opentelemetry import trace
import logging

logger = logging.getLogger(__name__)

class Feedback:
    def __init__(self, message_idx):
        self.message_idx = message_idx
        self.key_prefix = f"feedback_{message_idx}"
        try:
            self.current_span = trace.get_current_span()
            self.span_id = None
            if self.current_span:
                self.span_id = self.current_span.get_span_context().span_id.to_bytes(8, "big").hex()
        except Exception as e:
            logger.warning(f"Failed to get trace span: {e}")
            self.current_span = None
            self.span_id = None

    def _send_phoenix_annotation(self, label: str, score: float, explanation: str = ""):
        """Send feedback annotation to Phoenix."""
        # Store feedback locally even if Phoenix is not available
        feedback_data = {
            "label": label,
            "score": score,
            "explanation": explanation,
            "timestamp": time.time()
        }
        if not hasattr(st.session_state, 'feedback_store'):
            st.session_state.feedback_store = []
        st.session_state.feedback_store.append(feedback_data)

        # Try to send to Phoenix if tracing is available
        if self.span_id:
            try:
                client = httpx.Client(timeout=5.0)
                logger.info(f"Sending feedback to Phoenix server for span {self.span_id}")
                annotation_payload = {
                    "data": [{
                        "span_id": self.span_id,
                        "name": "user feedback",
                        "annotator_kind": "HUMAN",
                        "result": {
                            "label": label,
                            "score": score,
                            "explanation": explanation
                        },
                        "metadata": {}
                    }]
                }

                try:
                    phoenix_url = "http://0.0.0.0:6007/v1/span_annotations?sync=false"
                    logger.info(f"Connecting to Phoenix server at {phoenix_url}")
                    response = client.post(
                        phoenix_url,
                        json=annotation_payload,
                        headers={"Content-Type": "application/json"}
                    )
                    if response.status_code != 200:
                        logger.warning(f"Phoenix server returned status {response.status_code}: {response.text}")
                except httpx.RequestError as e:
                    logger.warning(f"Could not connect to Phoenix server: {e}")
            except Exception as e:
                logger.warning(f"Failed to send feedback to Phoenix: {e}")

        return True

    def render(self):
        """Render feedback buttons and text input."""
        st.markdown("##### How was this response?")

        # Thumbs up/down buttons in a row
        col1, col2, _ = st.columns([1, 1, 4])
        with col1:
            if st.button("👍", key=f"{self.key_prefix}_up"):
                st.session_state.chat_history[self.message_idx]["feedback"] = {
                    "rating": "positive",
                    "text": st.session_state.get(f"{self.key_prefix}_text", "")
                }
                self._send_phoenix_annotation("thumbs_up", 1.0)
                st.success("Thanks for the positive feedback!")

        with col2:
            if st.button("👎", key=f"{self.key_prefix}_down"):
                st.session_state.chat_history[self.message_idx]["feedback"] = {
                    "rating": "negative",
                    "text": st.session_state.get(f"{self.key_prefix}_text", "")
                }
                self._send_phoenix_annotation("thumbs_down", 0.0)
                st.error("Thanks for the feedback! Please let us know how we can improve.")

        # Text feedback in a separate container
        with st.container():
            st.markdown("##### Additional Comments (optional)")
            feedback_text = st.text_area(
                "Share your thoughts about this response",
                key=f"{self.key_prefix}_text",
                label_visibility="collapsed",
                placeholder="Enter your feedback here..."
            )

            if st.button("Submit Feedback", key=f"{self.key_prefix}_submit"):
                if feedback_text:
                    if "feedback" in st.session_state.chat_history[self.message_idx]:
                        st.session_state.chat_history[self.message_idx]["feedback"]["text"] = feedback_text
                        score = 1.0 if st.session_state.chat_history[self.message_idx]["feedback"].get("rating") == "positive" else 0.0
                        self._send_phoenix_annotation("text_feedback", score, feedback_text)
                        st.success("Thank you for your detailed feedback!")
                    else:
                        st.session_state.chat_history[self.message_idx]["feedback"] = {
                            "rating": None,
                            "text": feedback_text
                        }
                        self._send_phoenix_annotation("text_feedback", 0.5, feedback_text)
                        st.success("Thank you for your feedback!")
                else:
                    st.info("Please enter some feedback text before submitting.")

class ChatInterface:
    def __init__(self):
        self.rag_system = st.session_state.rag_system

    def _display_message(self, role, content, message_idx=None):
        """Display a chat message with appropriate styling."""
        with st.chat_message(role):
            st.markdown(content)
            if role == "assistant" and message_idx is not None:
                st.markdown("---")  # Add a separator line
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