import streamlit as st
from chat import ChatInterface
from rag import RagSystem
import logging
import os
import sys

from phoenix.otel import register
from openinference.instrumentation.openai import OpenAIInstrumentor

tracer_provider = register()
OpenAIInstrumentor().instrument(tracer_provider=tracer_provider)

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stdout
)
logger = logging.getLogger(__name__)

logger.info("Starting Roman Empire Chat application...")
logger.info(f"Current working directory: {os.getcwd()}")
logger.info(f"Python path: {sys.path}")

st.set_page_config(
    page_title="Roman Empire Chat",
    page_icon="🏛️",
    layout="wide"
)

def main():
    try:
        logger.info("Initializing session state...")
        if 'chat_history' not in st.session_state:
            st.session_state.chat_history = []

        if 'rag_system' not in st.session_state:
            logger.info("Initializing RAG system...")
            st.session_state.rag_system = RagSystem()
            logger.info("RAG system initialized successfully")

        st.title("🏛️ Roman Empire Chat")
        st.markdown("""
        Ask questions about the Roman Empire! This chatbot uses information from Wikipedia 
        to provide accurate answers about Roman history, culture, and more.
        """)

        logger.info("Creating chat interface...")
        chat_interface = ChatInterface()

        col1, col2 = st.columns([6, 1])
        with col2:
            if st.button("Clear Chat"):
                st.session_state.chat_history = []
                st.experimental_rerun()

        chat_interface.render()
    except Exception as e:
        logger.error(f"Error in main function: {str(e)}", exc_info=True)
        st.error("An error occurred while starting the application. Please check the logs for details.")
        raise

if __name__ == "__main__":
    try:
        logger.info("Checking environment variables...")
        logger.info(f"OPENAI_API_KEY present: {bool(os.environ.get('OPENAI_API_KEY'))}")

        if not os.environ.get("OPENAI_API_KEY"):
            logger.error("OpenAI API key is not set in environment variables")
            st.error("OpenAI API key is not set. Please set the OPENAI_API_KEY environment variable.")
        else:
            logger.info("Starting main application...")
            main()
    except Exception as e:
        logger.error(f"Application startup error: {str(e)}", exc_info=True)
        st.error("Failed to start the application. Please check the logs for details.")
        raise
