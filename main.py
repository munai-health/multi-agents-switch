from tools.get_encounter_info import get_encounter_info
from tools.fhir_parser import parse_encounter_data
from typing import TypedDict

from langgraph.graph import StateGraph, END

from agents.summary import summarize_patient
from agents.investigator import exec_investigator
from agents.decision_maker import exec_decision_maker
from agents.reviewer import exec_reviewer
from agents.curator import exec_curator
import sys



class PipelineState(TypedDict):
    encounter_id: str

    patient_summary: str
    investigation_report: str

    output_decision_maker: str
    output_reviewer: str

    final_decision: str


def node_summary(state: PipelineState) -> dict:
    """Call Summary Tool to get patient summary."""

    print(f"[Summary] Getting Patient Summary {state['encounter_id']}...")

    encounter_data = get_encounter_info(state["encounter_id"])
    
    parsed = parse_encounter_data(encounter_data)
    
    resumo = summarize_patient(parsed)
    
    return {"patient_summary": resumo}



def node_investigador(state: PipelineState) -> dict:
    """Execute the Investigator agent with a ReAct loop over the Pinecone vector store to extract relevant clinical criteria for the patient."""
    print("[Investigator] Searching for relevant clinical criteria...")

    report = exec_investigator(state["patient_summary"])

    return {"investigation_report": report}


def node_decision_maker(state: PipelineState) -> dict:
    """Execute the Decision Maker agent to produce a clinical assessment based on the patient summary and investigation report."""
    print("[Decision Maker] Generating clinical assessment...")

    output = exec_decision_maker(
        state["patient_summary"],
        state["investigation_report"],
    )
    return {"output_decision_maker": output}


def node_reviewer(state: PipelineState) -> dict:
    """Execute the Reviewer agent to identify any potential safety concerns or contraindications for switching from IV to oral antibiotic therapy based on the patient summary and investigation report."""
    print("[Reviewer] Searching for safety concerns...")

    output = exec_reviewer(
        state["patient_summary"],
        state["investigation_report"],
    )
    return {"output_reviewer": output}


def node_curator(state: PipelineState) -> dict:
    """Execute the Curator agent to synthesize the assessments from the Decisor and Revisor into a final decision."""

    print("[Curator] Synthesizing final decision...")

    decision = exec_curator(
        state["patient_summary"],
        state["investigation_report"],
        state["output_decision_maker"],
        state["output_reviewer"],
    )
    return {"final_decision": decision}


def build_pipeline():
    graph = StateGraph(PipelineState)

    graph.add_node("summary", node_summary)
    graph.add_node("investigator", node_investigador)
    graph.add_node("decision_maker", node_decision_maker)
    graph.add_node("reviewer", node_reviewer)
    graph.add_node("curator", node_curator)

    graph.set_entry_point("summary")
    graph.add_edge("summary", "investigator")
    graph.add_edge("investigator", "decision_maker")
    graph.add_edge("investigator", "reviewer")
    graph.add_edge("decision_maker", "curator")
    graph.add_edge("reviewer", "curator")
    graph.add_edge("curator", END)

    return graph.compile()

def evaluate_patient(encounter_id: str) -> dict:
    """
    Execute the entire pipeline to evaluate whether a hospitalized patient should be switched from intravenous to oral antibiotic therapy based on the encounter ID.
    """

    initial_state: PipelineState = {
        "encounter_id": encounter_id,
        "patient_summary": "",
        "investigation_report": "",
        "output_decision_maker": "",
        "output_reviewer": "",
        "final_decision": "",
    }

    result = pipeline.invoke(initial_state)

    return {
        "encounter_id": encounter_id,
        "patient_summary": result["patient_summary"],
        "investigation_report": result["investigation_report"],
        "output_decisor": result["output_decision_maker"],
        "output_reviewer": result["output_reviewer"],
        "final_decision": result["final_decision"],
    }


if __name__ == "__main__":

    pipeline = build_pipeline()

    if len(sys.argv) < 2:
        print("Usage: python main.py <encounter_id>")
        sys.exit(1)

    encounter_id = sys.argv[1]
    print(f"\n{'=' * 60}")
    print(f"  Evaluating Patient Encounter ID: {encounter_id}")
    print(f"{'=' * 60}\n")

    result = evaluate_patient(encounter_id)

    print("\n" + "=" * 60)
    print("  PATIENT SUMMARY ")
    print("=" * 60)
    print(result["patient_summary"])

    print("\n" + "=" * 60)
    print("  INVESTIGATION_REPORT ")
    print("=" * 60)
    print(result["investigation_report"])

    print("\n" + "=" * 60)
    print("  DECISION MAKER OUTPUT ")
    print("=" * 60)
    print(result["output_decisor"])

    print("\n" + "=" * 60)
    print("  REVIEWER OUTPUT ")
    print("=" * 60)
    print(result["output_reviewer"])

    print("\n" + "=" * 60)
    print("  FINAL DECISION ")
    print("=" * 60)
    print(result["final_decision"])
