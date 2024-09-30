###----------------------------------
###  Python Modules
###----------------------------------
from core import *
import streamlit as st

###----------------------------------------------
### - Streamlit
###----------------------------------------------
def app():
    st.markdown("### Multi-Agent RAG")
    st.markdown("""
    <style>
    .stRadio > div { margin-top: -20px; } /* Adjust the margin-top value */
    </style>
    """, unsafe_allow_html=True)
    
    # Initialize the chat history if it doesn't exist
    if 'messages' not in st.session_state:
        st.session_state['messages'] = []

    # Input for new question
    question = st.chat_input("Enter a topic")
    
    if debug_mode: print("Its in debug mode")

    if question:
        # Add the user's question to the chat history
        st.session_state['messages'].append({"role": "user", "content": question})

        # Process the question
        response = processflow_graph_invoke(question)

        # Add the assistant's response to the chat history
        st.session_state['messages'].append({"role": "assistant", "content": response["output"]})
        
        # Parse the response and display it as a table
        if "||" in response:  # Example delimiter to check for Markdown table
            st.markdown("### Comparison Table")
            st.markdown(response)  # Display the raw Markdown response

    # Display the chat history
    for message in st.session_state['messages']:
        if message["role"] == "user":
            st.chat_message("user").markdown(message["content"])
        else:
            st.chat_message("assistant").markdown(message["content"])
