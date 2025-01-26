import streamlit as st
from chat import ChatInterface
from rag import RagSystem

# Page config
st.set_page_config(
    page_title="Roman Empire Chat",
    page_icon="🏛️",
    layout="wide"
)

def main():
    # Initialize session state
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    
    if 'rag_system' not in st.session_state:
        st.session_state.rag_system = RagSystem()

    # Title and description
    st.title("🏛️ Roman Empire Chat")
    st.markdown("""
    Ask questions about the Roman Empire! This chatbot uses information from Wikipedia 
    to provide accurate answers about Roman history, culture, and more.
    """)

    # Create chat interface
    chat_interface = ChatInterface()
    
    # Add a clear button
    col1, col2 = st.columns([6, 1])
    with col2:
        if st.button("Clear Chat"):
            st.session_state.chat_history = []
            st.experimental_rerun()

    # Display chat interface
    chat_interface.render()

if __name__ == "__main__":
    main()
