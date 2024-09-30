import os
import streamlit as st
from core import *

def app():
    st.markdown("### Audio File Ingestion")
        
    st.markdown("""
    <style>
    .stRadio > div { margin-top: -20px; } /* Adjust the margin-top value */
    </style>
    """, unsafe_allow_html=True)
    
    dataSourceDir="./datasets/short-stories/"
    
    if 'ingest_status' not in st.session_state:
        st.session_state['ingest_status'] = None
    
    # Create three columns
    col1, col2, col3 = st.columns([2, 1, 5])

    # Left Column - List of Audio Files
    with col1:
        st.write("Audio Files:")
        if not os.path.exists(dataSourceDir):
            abortProcess(f"Path-{dataSourceDir} does not exists")
            
        for file in os.listdir(dataSourceDir):
            st.write(f"- {file}")

    # Center Column - Ingest Button
    with col2:
        if st.session_state['ingest_status'] == "Running":
            st.write("Data Ingestion is in progress")
        elif st.button("Ingest Audio Files"):
            st.session_state['ingest_status'] = "Running"
            ingestAudio(dataSourceDir)
            st.session_state['ingest_status'] = "Completed"
            st.experimental_rerun()

    # Right Column - Elasticsearch Document Count
    with col3:        
        es_client=getOrCreate_es_client()
        
        if not es_client.indices.exists(index=elastic_index_name):
            st.error(f"{elastic_index_name} does not exists")
        else:
            doc_count = get_document_count()
            one_doc = get_one_document()

def get_document_count():
    es_client=getOrCreate_es_client()
    try:
        doc_count = es_client.count(index=elastic_index_name)['count']
        st.write(f"Index: '{elastic_index_name}' has {doc_count} records")
    except Exception as e:
        st.error(f"Error fetching document count: {e}")

def get_one_document():
    es_client=getOrCreate_es_client()
    try:
        doc = es_client.search(index=elastic_index_name, size=1)
        st.json(doc["hits"]["hits"][0]["_source"]) if doc["hits"]["total"]["value"] > 0 else st.error("No documents found")
    except Exception as e:
        st.error(f"Error fetching document: {e}")