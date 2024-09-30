###----------------------------------
###  Python Modules
###----------------------------------
from core import *
import getopt
from typing import TypedDict
from langgraph.graph import StateGraph, END

###----------------------------------------------
### - User Dialogue Graph
###----------------------------------------------
class input_dataType(TypedDict):
    input: str
    isUserEngaged: bool

def input_prompt(state: input_dataType) -> input_dataType:
    input_prompt = input("\n Input Prompt ('q' to quit) : ")
    return {
        "input": input_prompt,
        "isUserEngaged": input_prompt.lower() not in ('q', '')
    }

def prompt_handler(state: input_dataType):
    processflow_graph = create_processflow_graph()
    response = processflow_graph.invoke({"input": state["input"]})
    print("\nAI Response")
    print(response["output"])
    return state

def create_dialogue_graph():
    workflow = StateGraph(input_dataType)

    workflow.add_node("input_prompt", input_prompt)
    workflow.add_node("prompt_handler", prompt_handler)

    workflow.add_conditional_edges(
        "input_prompt",
        lambda x: "active" if x["isUserEngaged"] else "end",
        {
            "active": "prompt_handler",
            "end": END
        }
    )
    
    workflow.set_entry_point("input_prompt")
    workflow.add_edge("prompt_handler", "input_prompt")

    return workflow.compile()

###----------------------------------------------
### - Main Module
###----------------------------------------------
def print_help():
    help_text = """
    Usage: python3 your_script.py [options]

    Options:
    -i, --ingest <directory>    Ingest audio data from the specified directory.
    -g, --invoke                Invoke the dialogue graph.
    -h, --help                  Show this help message and exit.

    Notes:
    - You cannot use both --ingest and --invoke options together.
    - If using the --ingest option, the directory path is required.
    """
    print(help_text)
    
def main(argv):    
    if len(argv)<1:
        print_help()
        sys.exit(1)
        
    try:
        opts, args = getopt.getopt(argv, "i:g", ["ingest=", "invoke"])
    except getopt.GetoptError as err:
        print(f"Error: {err}")
        print_help()
        sys.exit(1)

    ingest_option = None
    invoke_option = False

    for opt, arg in opts:
        if opt in ("-i", "--ingest"):
            ingest_option = arg  # Store the directory path
        elif opt in ("-g", "--invoke"):
            invoke_option = True

    if ingest_option and invoke_option:
        print("Error: Cannot ingest data and invoke graph at the same time.")
        sys.exit(1)

    if ingest_option:
        if not ingest_option:  # Path must be provided with the ingest option
            print("Error: Input path not provided for ingest.")
            sys.exit(1)
        else:
            dataSourceDir = ingest_option
            ingestAudio(dataSourceDir)
    elif invoke_option:
        dialogue_graph = create_dialogue_graph()
        dialogue_graph.invoke({"input": "", "isUserEngaged": True})
    else:
        print("Error: No valid option selected. Use -i for ingest or -g for invoke.")
        sys.exit(1)

if __name__ == "__main__":
    main(sys.argv[1:])