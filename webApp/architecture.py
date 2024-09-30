import streamlit as st
import importlib, inspect
    
def display_function_code(functions):
    cols = st.columns(len(functions))
    for idx, (module_name, function_name) in enumerate(functions):
        with cols[idx]:
            try: 
                module = importlib.import_module(module_name)
                func = getattr(module, function_name)
                source_code = inspect.getsource(func)
                st.code(source_code, language="python")
            except ModuleNotFoundError:
                st.write(f"Module '{module_name}' not found.")
            except Exception as e:
                st.write(f"Error: {e}")

def app():
    st.markdown("""
    ### System HL Overview
    1. **Data Ingestion Layer**: 
       This layer leverages Hugging Face Transformers and OpenAI's Whisper Medium to transcribe audio files into text. The text is then transformed into vector embeddings using ELSER, and these embeddings are ingested into Elastic Cloud for further processing.
    
    2. **Multi-Agent Inference Layer**: 
       This layer is powered by LangGraph integrated with the Elastic Search Relevance Engine (ESRE) and Azure OpenAI's LLM.
       It comprises three Agents: router agent, RAG analyzer agent, and RAG comparer agent. 
       The router agent serves as the initial point of contact, directing the workflow by passing control to the appropriate agent based on its assessment.
       Both the RAG analyzer and RAG comparer agents execute semantic searches to retrieve relevant contextual information related to the input query, which is then provided to the LLM to generate new content.

    3. **User Interface**: 
       The application is entirely wrapped in to a Streamlit app.
    """)
    st.markdown("### Architecture Diagram")

    st.image("static_data/arch.png", caption="System Architecture Diagram", width=1000)
    
    components = {
        "1.Speech2Text":        {"functions": [("core.utility", "speech2Text")],
                                 "links": [("[HuggingFace-Transformers](https://huggingface.co/openai/whisper-medium)")]},
        "2.Elastic Learned Sparse EncodeR (ELSER)":
                                {"functions": [("core.utility", "ingest_into_elastic"),
                                               ("core.utility", "create_index_in_elastic")],
                                 "links": [("[ELSER](https://www.elastic.co/guide/en/machine-learning/current/ml-nlp-elser.html)"),
                                          ("[Semantic_text](https://www.elastic.co/guide/en/elasticsearch/reference/current/semantic-search-semantic-text.html)"),
                                          ("[Simplifying Semantic Search](https://www.elastic.co/search-labs/blog/semantic-search-simplified-semantic-text)")]},
        "3.Elastic Cloud":      {"functions": [],
                                 "links": [("[ElasticCloud-FreeTrial](https://www.elastic.co/cloud/elasticsearch-service/signup?page=docs&placement=docs-body)"),
                                           ("[Elastic Hosted Deployment](https://www.elastic.co/guide/en/cloud/current/ec-create-deployment.html)"),
                                           ("[ElasticSearch Cluster API Key](https://www.elastic.co/guide/en/kibana/current/api-keys.html)"),
                                           ("[ELSER inference service](https://www.elastic.co/guide/en/elasticsearch/reference/current/infer-service-elser.html)"),
                                           ("[Azure OpenAI](https://learn.microsoft.com/en-us/azure/ai-services/openai/how-to/create-resource?pivots=web-portal)")]},
        "4.LangGraph":          {"functions": [("core.agentTemplates", "create_processflow_graph"),
                                               ("core.agentTemplates", "agent_dataType"),
                                               ("core.agentTemplates", "processflow_graph_invoke")],
                                 "links": [("[LangGraph](https://langchain-ai.github.io/langgraph/tutorials/multi_agent/multi-agent-collaboration/)")]},
        "5.Router Agent":       {"functions": [("core.agentTemplates", "routerAgent"), ("core.promptTemplates", "routerPrompt")],
                                 "links": []},
        "6.RAG Analyzer Agent": {"functions": [("core.agentTemplates", "ragAnalyzerAgent"), ("core.promptTemplates", "ragAnalyzerPrompt")],
                                 "links": []},
        "7.Elastic Search Relevance Engine (ESRE)":
                                {"functions": [("core.utility", "semanting_search_with_rrf"), 
                                               ("core.utility", "getOrCreate_retriever")],
                                 "links": [("[ESRE](https://www.elastic.co/guide/en/esre/current/learn.html)"),
                                           ("[Elastic Retrievers](https://www.elastic.co/guide/en/elasticsearch/reference/current/retrievers-overview.html)"),
                                           ("[Search Relevance Tuning](https://www.elastic.co/search-labs/blog/search-relevance-tuning-in-semantic-search)"),
                                           ("[Eland](https://www.elastic.co/guide/en/machine-learning/8.15/ml-nlp-import-model.html)")]},
        "8.RAG Comparer Agent": {"functions": [("core.agentTemplates", "ragComparerAgent"), ("core.promptTemplates", "ragComparerPrompt")],
                                 "links": [("[HuggingFace-Transformers](https://huggingface.co/openai/whisper-medium)")]}
        }

    st.markdown("### Select a Component to Learn More")
    selected_component = st.radio("Click on a component", options=list(components.keys()), label_visibility="hidden")

    # Display information based on the selected component
    if selected_component:
        subheader_text= f"{selected_component.split('.')[1]} Component : " \
                        f"<span style='font-size: 16px;'>" \
                        f"{' | '.join(components[selected_component]['links'])}</span>"
        st.markdown(subheader_text, unsafe_allow_html=True)
        functions = components[selected_component]['functions']
        if len(functions)>0:
            display_function_code(functions)