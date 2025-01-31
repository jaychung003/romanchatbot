import os
import streamlit as st
from rag import RagSystem
import time
import httpx
import logging
from opentelemetry import trace

logger = logging.getLogger(__name__)


class Feedback:
    def __init__(self, message_idx):
        self.message_idx = message_idx
        self.key_prefix = f"feedback_{message_idx}"
        
        logger.info(f"📝 Chat history at index {message_idx}: {st.session_state.chat_history[message_idx]}")
        
        self.span_id = st.session_state.chat_history[self.message_idx].get("span_id")
        if not self.span_id:
            logger.warning(f"⚠️ No valid span ID found for message {message_idx}")
        else:
            logger.info(f"✅ Retrieved valid span_id: {self.span_id}")

    def _send_phoenix_annotation(self, label: str, score: float, explanation: str = ""):
        """Send feedback annotation to Phoenix."""
        if not self.span_id:
            logger.warning("⚠️ Skipping feedback annotation: No valid span ID available.")
            return False

        feedback_data = {
            "label": label,
            "score": score,
            "explanation": explanation,
            "timestamp": time.time()
        }
        
        st.session_state.setdefault("feedback_store", []).append(feedback_data)

        try:
            client = httpx.Client(timeout=5.0)
            logger.info(f"📡 Sending feedback to Phoenix server for span {self.span_id}")
            
            annotation_payload = {
                "data": [{
                    "span_id": self.span_id,
                    "name": "user_feedback",
                    "annotator_kind": "HUMAN",
                    "result": {
                        "label": label,
                        "score": score,
                        "explanation": explanation
                    },
                    "metadata": {}
                }]
            }

            response = client.post(
                "http://0.0.0.0:6006/v1/span_annotations?sync=false",
                json=annotation_payload,
                headers={"Content-Type": "application/json"}
            )

            if response.status_code == 200:
                logger.info("✅ Successfully sent feedback to Phoenix server")
            else:
                logger.warning(f"⚠️ Phoenix server returned status {response.status_code}: {response.text}")

        except httpx.RequestError as e:
            logger.warning(f"⚠️ Could not connect to Phoenix server: {e}")
        return True

    def render(self):
        """Render feedback buttons and text input."""
        st.markdown("##### How was this response?")
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

        feedback_text = st.text_area(
            "Share your thoughts about this response",
            key=f"{self.key_prefix}_text",
            label_visibility="collapsed",
            placeholder="Enter your feedback here..."
        )

        if st.button("Submit Feedback", key=f"{self.key_prefix}_submit"):
            if feedback_text:
                feedback = st.session_state.chat_history[self.message_idx].setdefault("feedback", {})
                feedback["text"] = feedback_text
                score = 1.0 if feedback.get("rating") == "positive" else 0.0
                self._send_phoenix_annotation("text_feedback", score, feedback_text)
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
                logger.info(f"🛠️ Creating Feedback instance for message index: {message_idx}")
                Feedback(message_idx).render()

    def _process_user_input(self, user_input: str) -> str:
        """Process user input and get response from RAG system."""
        try:
            with st.spinner("Thinking..."):
                logger.info(f"📝 Chat history BEFORE processing input: {st.session_state.chat_history}")

                with trace.get_tracer(__name__).start_as_current_span("RAG Query Processing") as span:
                    span.set_attribute("rag.query", user_input)
                    response = self.rag_system.get_response(user_input)
                    span_id = span.get_span_context().span_id
                    span_id = None if span_id == 0 else span_id.to_bytes(8, "big").hex()
                    
                    message_entry = {
                        "role": "assistant",
                        "content": response,
                        "feedback": {"rating": None, "text": ""},
                        "span_id": span_id
                    }
                    
                    st.session_state.chat_history.append(message_entry)
                    logger.info(f"✅ Stored assistant response: {message_entry}")
                
                logger.info(f"📝 Chat history AFTER processing input: {st.session_state.chat_history}")
                return response
        except Exception as e:
            logger.error(f"❌ Error getting response: {str(e)}", exc_info=True)
            st.error("I encountered an error. Please try again.")
            return "I apologize, but I encountered an error while processing your question. Please try again."

    def render(self):
        """Render the chat interface."""
        for i, message in enumerate(st.session_state.chat_history):
            self._display_message(
                message["role"], message["content"],
                i if message["role"] == "assistant" else None
            )

        if user_input := st.chat_input("Ask a question about the Roman Empire"):
            st.session_state.chat_history.append({"role": "user", "content": user_input})
            self._display_message("user", user_input)
            response = self._process_user_input(user_input)
            self._display_message("assistant", response, len(st.session_state.chat_history) - 1)
