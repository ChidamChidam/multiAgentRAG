import os
from langchain_openai import AzureChatOpenAI
from langchain.prompts import PromptTemplate
from .utility import *
from .promptTemplates import *
from langchain_core.runnables import RunnableLambda
from typing import TypedDict
from langgraph.graph import StateGraph, END

llm = AzureChatOpenAI(azure_deployment=azure_openai_model_id, api_version=azure_openai_api_version,temperature=azure_openai_temperature)

###----------------------------------------------
### - ProcessFlow Graph
###----------------------------------------------
class agent_dataType(TypedDict):
    input: str
    output: str

def create_processflow_graph():
    workflow = StateGraph(agent_dataType)

    workflow.add_node("router",      routerAgent)
    workflow.add_node("raganalyzer", ragAnalyzerAgent)
    workflow.add_node("ragcomparer", ragComparerAgent)

    workflow.add_conditional_edges(
        "router",
        lambda x: x["output"].split(",")[0].strip(),
        {
            "compare": "ragcomparer",
            "analyze": "raganalyzer",
            "unknown": END
        }
    )

    workflow.set_entry_point("router")
    workflow.add_edge("raganalyzer", END)
    workflow.add_edge("ragcomparer", END)

    return workflow.compile()

def processflow_graph_invoke(question):
    processflow_graph = create_processflow_graph()
    return processflow_graph.invoke({"input": question})

###----------------------------------------------
### - Agent Template
###----------------------------------------------
def routerAgent(state):
    prompt = PromptTemplate.from_template(routerPrompt())
    chain = prompt | llm
    response = chain.invoke({"input": state["input"]})
    output = response.content.strip().lower()
    print(f"Router decision: {output}")
    return {"input": state["input"], "output": output}

def ragAnalyzerAgent(state):
    prompt = PromptTemplate.from_template(ragAnalyzerPrompt())
    chain = (
        {"context": getOrCreate_retriever() | format_docs,
        "question": RunnableLambda(lambda x: state["input"])}
        | prompt
        | RunnableLambda(lambda x: (print(f"Prompt passed to LLM: {x}") if debug_mode else None) or x)
        | llm  
        )
    if debug_mode: print(f'Rag input: {state["output"].split(",")[1].strip()}')
    response = chain.invoke({"search_query" : state["output"].split(",")[1].strip(), "size" : 1})
    if debug_mode: print(f"ragAnalyzerAgent Output: {response}")
    output_content = response.content if hasattr(response, 'content') else response
    return {"output": output_content}

def ragComparerAgent(state):
    prompt = PromptTemplate.from_template(ragComparerPrompt())
    chain = (
        {"context": getOrCreate_retriever() | format_docs,
         "question": RunnableLambda(lambda x: state["input"])}
        | prompt
        | RunnableLambda(lambda x: (print(f"Prompt passed to LLM: {x}") if debug_mode else None) or x)
        | llm  
        )
    if debug_mode: print(f'Rag input: {state["output"].split(",")[1].strip()}')
    response = chain.invoke({"search_query" : state["output"].split(",")[1].strip(), "size" : 2})
    if debug_mode: print(f"ragComparerAgent Output: {response}")
    output_content = response.content if hasattr(response, 'content') else response
    return {"output": output_content}