
from typing import Annotated
from typing_extensions import TypedDict
 
from langchain_core.messages import SystemMessage, HumanMessage, BaseMessage
from langchain_core.messages import ToolMessage
from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages
from langchain_core.runnables import RunnableConfig
 
from config import llm_investigator, MAX_INVESTIGATOR_ITERATIONS
from tools.pinecone_tool import search_criteria

SYSTEM_PROMPT = """
# You are a clinical investigator agent specialized in antibiotic therapy.

## Objective
Your task is to gather evidence from medical guidelines to assess whether a patient is suitable for switching from intravenous to oral antibiotics (IV-to-oral switch).

## Available Tool
You have access to the `search_criteria` tool, which queries indexed clinical guidelines.  
Use this tool as many times as necessary to cover all relevant criteria.

## Mandatory Topics
You MUST search for information on each of the following:

1. General clinical stability criteria for IV-to-oral switch  
2. Criteria for a functional oral route (swallowing, gastrointestinal absorption)  
3. Absolute contraindications to oral switch  
4. Criteria specific to the type of infection identified in the patient  
5. Relevant laboratory parameters:
   - Leukocytes  
   - C-reactive protein (CRP)  
   - Procalcitonin  
6. Vital sign parameters:
   - Fever  
   - Blood pressure  
   - Heart rate  

## Output Format
After investigating all topics, produce a structured report including:

- **Criteria that SUPPORT the switch**
- **Criteria that CONTRAINDICATE the switch**
- **Information gaps** (criteria that cannot be verified with the patient’s data)
- **Sources consulted**

## Constraints
- Be objective  
- Base your analysis ONLY on information found in the guidelines  
- Do NOT provide opinions  
"""

# -------
# Node 1
# -------

class InvestigatorState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]
    
# llm will decide if will use the tool or not
llm_with_tool = llm_investigator.bind_tools([search_criteria])

def call_model(state: InvestigatorState) -> dict:
    messages = state["messages"]
    response = llm_with_tool.invoke(messages)
    return {"messages": [response]}

# -------
# Node 2
# -------

def call_tools(state: InvestigatorState) -> dict:
    last_message = state["messages"][-1]
    tool_messages = []
 
    for tool_call in last_message.tool_calls:
        if tool_call["name"] == "search_criteria":
            resultado = search_criteria.invoke(tool_call["args"])
            
            tool_messages.append(
                ToolMessage(
                    content=resultado,
                    tool_call_id=tool_call["id"], 
                )
            )
 
    return {"messages": tool_messages}

# -------
# Router
# -------

def should_continue(state: InvestigatorState) -> str:
    last_message = state["messages"][-1]
 
    iteracoes = sum(1 for m in state["messages"] if isinstance(m, ToolMessage))
 
    if iteracoes >= MAX_INVESTIGATOR_ITERATIONS:
        return END  
 
    if hasattr(last_message, "tool_calls") and last_message.tool_calls:
        return "call_tools"
 
    return END

# -------
# Building Graph
# -------

def build_investigator():
    graph = StateGraph(InvestigatorState)
 
    graph.add_node("call_model", call_model)
    graph.add_node("call_tools", call_tools)
 
    graph.set_entry_point("call_model")
 
    graph.add_conditional_edges("call_model", should_continue)
 
    graph.add_edge("call_tools", "call_model")
 
    return graph.compile()
 
# -------
# Public Interface
# ------- 

investigator_graph = build_investigator()

def exec_investigator(patient_summary: str) -> str:
    """
    Executes the clinical investigator agent for a patient.

    Args:
        resumo_paciente: narrative text returned by Lucas's tool

    Returns:
        Structured report with criteria identified from clinical guidelines
    """
    
    initial_state = {
        "messages": [
            SystemMessage(content=SYSTEM_PROMPT),
            HumanMessage(content=f"Analyze the patient below and investigate the criteria for IV-to-oral switch.:\n\n{patient_summary}"),]
    }
    
    result = investigator_graph.invoke(initial_state)
    
    return result["messages"][-1].content