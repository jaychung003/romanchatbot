import streamlit as st

def apply_custom_styles():
    """Apply custom CSS styles to the Streamlit app."""
    st.markdown("""
        <style>
        .stChatMessage {
            padding: 1rem;
            border-radius: 0.5rem;
            margin-bottom: 1rem;
            max-width: 800px;
        }
        
        .stChatMessage [data-testid="chatAvatarIcon"] {
            background-color: #FF4B4B;
        }
        
        .stTextInput {
            max-width: 800px;
        }
        
        .stSpinner {
            text-align: center;
            margin: 1rem 0;
        }
        
        .stAlert {
            max-width: 800px;
        }
        </style>
    """, unsafe_allow_html=True)
