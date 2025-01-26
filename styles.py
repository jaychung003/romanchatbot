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

        /* Feedback styles */
        button[data-testid="baseButton-secondary"] {
            border-radius: 50%;
            width: 40px !important;
            height: 40px !important;
            padding: 0 !important;
            line-height: 40px;
            text-align: center;
            font-size: 1.2rem;
        }

        .feedback-section {
            margin-top: 0.5rem;
            padding-top: 0.5rem;
            border-top: 1px solid rgba(49, 51, 63, 0.1);
        }

        .feedback-input {
            margin-top: 0.5rem;
        }
        </style>
    """, unsafe_allow_html=True)