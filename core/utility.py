import configparser
import os, sys, time, json
from dotenv import load_dotenv
from elasticsearch import Elasticsearch
from langchain_elasticsearch import ElasticsearchRetriever
from typing import Dict, TypedDict
from langgraph.graph import StateGraph, END

###------------------------------------------------------------------------------
###   Set Environment and Application Variables 
###------------------------------------------------------------------------------
def getEnvVariables():
    load_dotenv()
    
def getConfigData():
    config = configparser.ConfigParser()
   
    config_path = os.path.join(os.path.dirname(__file__),'config.ini')
    if not os.path.isfile(config_path): abortProcess(f"ConfigFile: {config_path} not found")
   
    config.read(config_path)
   
    global elastic_index_name
    global elastic_model_id
    global azure_openai_model_id
    global azure_openai_api_version
    global azure_openai_temperature
    global debug_mode

    try:
        elastic_index_name = config.get('ELASTIC','INDEX_NAME')
        elastic_model_id = config.get('ELASTIC','MODEL_ID')
        azure_openai_model_id = config.get('AZURE_OPENAI', 'MODEL_ID')
        azure_openai_api_version = config.get('AZURE_OPENAI', 'API_VERSION')
        azure_openai_temperature = config.get('AZURE_OPENAI', 'TEMPERATURE')
    except Exception as e:
        abortProcess(e)
    
    debug_mode = os.getenv('debug', 'False').lower() in ('true', '1', 't', 'yes')

def validateVariables():
   pass

def abortProcess(msg):
    if 'streamlit' in sys.modules:
        import streamlit as st
        st.error(f"Error: {msg}")
    else:
        print(f"Error: {msg}")
        sys.exit(1)

###----------------------------------------------
### - Default Functions
###----------------------------------------------
es_client = None
getEnvVariables()
getConfigData()
from .agentTemplates import *

###------------------------------------------------------------------------------
###   OpenAI/Whisper-medium 
###------------------------------------------------------------------------------
def speech2Text():
    from transformers import pipeline, WhisperForConditionalGeneration, WhisperFeatureExtractor, WhisperTokenizer
    import torch
    device = torch.device("mps" if torch.backends.mps.is_available() else "cpu")
    
    feature_extractor = WhisperFeatureExtractor.from_pretrained("openai/whisper-medium")
    tokenizer = WhisperTokenizer.from_pretrained("openai/whisper-medium", language="en", task="transcribe")
    model = WhisperForConditionalGeneration.from_pretrained("openai/whisper-medium").to(device)
    forced_decoder_ids = tokenizer.get_decoder_prompt_ids(language="en", task="transcribe")

    transcribe_pipe = pipeline(
        "automatic-speech-recognition",
        model=model,
        feature_extractor=feature_extractor,
        tokenizer=tokenizer,
        device=0)
    
    return transcribe_pipe, forced_decoder_ids

###------------------------------------------------------------------------------
###   Elastic Search 
###------------------------------------------------------------------------------
def getOrCreate_es_client() -> Elasticsearch:
    global es_client
    
    if es_client is None or not es_client.ping():
        try:
            es_client = Elasticsearch(os.environ.get("ELASTIC_ENDPOINT"),
                                      api_key=os.environ.get("ELASTIC_API_KEY"))
        except Exception as e:
            abortProcess(f"unable to establish connection to ElasticSearch : {e}")
    return es_client

def create_index_in_elastic(elastic_index_name):
    es_client=getOrCreate_es_client()
    if not es_client.indices.exists(index=elastic_index_name):
        mappings = {
            "properties": {
                "content": {
                    "type": "text",
                    "copy_to": [ "semantic_data" ]
                    },
                "audio_id": { "type": "keyword"},
                "semantic_data": {
                    "type": "semantic_text",
                    "inference_id": "my-elser-model",
                    "model_settings": { "task_type": "sparse_embedding" }
                    }
                }
            }
        response=es_client.indices.create(index=elastic_index_name, mappings=mappings)
        return response.get('acknowledged')
    
def semanting_search_with_rrf(params: dict) -> Dict:
    query = {
        "retriever": {
            "rrf": {
                "retrievers": [
                    {
                        "standard": {
                            "query": {
                                "nested": {
                                    "path": "semantic_data.inference.chunks",
                                    "query": {
                                        "sparse_vector": {
                                            "inference_id": elastic_model_id,
                                            "field": "semantic_data.inference.chunks.embeddings",
                                            "query": params['search_query']
                                        }
                                    },
                                    "inner_hits": {
                                        "name": "semantic_data",
                                        "_source": ["semantic_data.inference.chunks.text"]
                                    }
                                }
                            }
                        }
                    },
                    {
                        "standard": {
                            "query": {
                                "match": {
                                    "content": params['search_query']
                                }
                            }
                        }
                    }
                ],
                "rank_window_size": 10
            }
        },
        "size": params['size']
    }
    if debug_mode: print(query)
    return query

def format_docs(docs):
    return "\n\n".join([d.page_content for d in docs])

def getOrCreate_retriever():
    retriever = ElasticsearchRetriever(
        es_client=getOrCreate_es_client(),
        index_name=elastic_index_name,
        content_field="content",
        body_func=semanting_search_with_rrf,
        )
    return retriever

def ingest_into_elastic(audio_in, transcribe_pipe, forced_decoder_ids):
    es_client=getOrCreate_es_client()
    
    ### Speech2Text
    speech2text_start_time = time.time()
    textContent=transcribe_pipe(audio_in, generate_kwargs={"forced_decoder_ids": forced_decoder_ids})['text']
    print(f"Feed: {audio_in}, Speech2Text ElaspedTime: {round(time.time() - speech2text_start_time)} seconds\nContent: {textContent}")

    ### Ingesting data into ElasticSearch
    ingest_start_time = time.time()
    doc = {'audio_id': os.path.basename(audio_in),
           'content': textContent
           }
    resp=es_client.index(index=elastic_index_name, body=json.dumps(doc))
    print(f"doc {resp['result']} in elastic, ElaspedTime: {round(time.time() - ingest_start_time)} seconds")
    
def ingestAudio(dataSourceDir):
    if not os.path.exists(dataSourceDir):
        abortProcess(f"Path-{dataSourceDir} does not exists")
        
    start_time = time.time()
    (transcribe_pipe, forced_decoder_ids)=speech2Text()
    
    create_index_in_elastic(elastic_index_name)
    
    for audio_feed in os.listdir(dataSourceDir):
        audio_in=f"{dataSourceDir}/{audio_feed}"
        print(f"Feed: {audio_in}")
        ingest_into_elastic(audio_in, transcribe_pipe, forced_decoder_ids)
    
    print(f"ElaspedTime: {round(time.time() - start_time)} seconds")

