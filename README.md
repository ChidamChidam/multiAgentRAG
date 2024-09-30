# Voices to Vectors: Multi-Agent : Semantic-Search

## Prerequisites

1. Elastic Cloud
    1. Create a Hosted Deployment (or) a Serverless Project
    2. Create ElasticSearch Cluster API KEY
    3. Create ELSER inference endpoint
2. Azure OpenAI LLM - EndPoint, Region, API Key, Version, ModelID
3. Python 3.12.6 or later

## Installation Steps

1. Clone this repo

2. Set the Python Environment
    ```bash
    python3 -m venv multiAgentRAG
    source multiAgentRAG/bin/activate
    pip install -r requirements
    ```
2. create "./core/.env" file and populate. you can use './core/.env.sample' as a example file
    ```bash
    ELASTIC_ENDPOINT="<Elastic Cloud EndPoint of your Deployment">
    ELASTIC_API_KEY="<ElasticSearch Cluster API Key that you created in your Deployment>"

    AZURE_OPENAI_API_KEY="<Azure OpenAI API Key>"
    AZURE_OPENAI_REGION="<Azure OpenAI Region>"
    AZURE_OPENAI_ENDPOINT="<Azure OpenAI Model Deployment Endpoint>"
    ```
3. Populate config.ini, you can also opt to go with the default config.ini settings
    ```bash
    [ELASTIC]
    INDEX_NAME="<Elastic Index Name>"
    MODEL_ID="<Elastic ELSER Inference ID>"

    [AZURE_OPENAI]
    MODEL_ID="<Azure OpenAI Model that you have deployed'>"
    API_VERSION="<Azure OpenAI Model version>"
    TEMPERATURE=0
    ```

6. Install [ffmpeg](https://www.ffmpeg.org/download.html) : ffmpeg is a OSS for video/audio processing
    ```bash
    # For MAC
    brew install ffmpeg
    # Check if its installed by running
    ffmpeg -version
    ```
## Running the Application

There are two ways to access the app
1. Web Access using Streamlit
    ```bash
    streamlit run main.py
    ```

2. Console access using console.py script
    ```bash
    python3 console.py -h
    
    # To ingest audio files into Elastic
    python3 console.py -i <data-path-dir>

    # To invoke multi-agent graph workflow
    python3 console.py -g 
    ```