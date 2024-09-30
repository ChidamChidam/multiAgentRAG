###----------------------------------
###  Python Modules
###----------------------------------
import os, importlib
import streamlit as st
st.set_page_config(layout="wide")

###----------------------------------------------
### - Streamlit
###----------------------------------------------
st.markdown("# Voices to Vectors: Multi-Agent RAG Workflow")
st.markdown("""
    <style>
    .stRadio > div { margin-top: -20px; } /* Adjust the margin-top value */
    </style>
    """, unsafe_allow_html=True)

# Sidebar for navigation
st.sidebar.title("Navigation")
pages = sorted([f.replace(".py", "") for f in os.listdir("webApp") if f.endswith(".py")])

# Sidebar radio button for page navigation
page_selection = st.sidebar.radio("Go To", pages, index=pages.index("architecture"), label_visibility="hidden")

# if page_selection == "ingestionLayer":
#     st.set_page_config(layout="wide")
# else:
#     st.set_page_config(layout="centered") 
    
# Dynamically import and load the selected page
selected_page = importlib.import_module(f"webApp.{page_selection}")
selected_page.app()
