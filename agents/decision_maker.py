from langchain_core.messages import SystemMessage, HumanMessage
from config import llm_decision_maker
 
# -------
# PROMPT 
# -------
# The Decison Maker receives rich context (patient summary + investigation report)
# and produces a balanced clinical analysis.

SYSTEM_PROMPT = """You are a senior infectious disease specialist evaluating whether
a hospitalized patient should be switched from intravenous to oral antibiotic therapy.
 
You will receive:
1. A clinical summary of the patient
2. An investigation report with criteria extracted from clinical guidelines
 
Your task is to produce a structured clinical assessment with the following sections:
 
## Criteria Met
List each guideline criterion that the patient satisfies, with brief justification
citing the patient's clinical data.
 
## Criteria Not Met
List each guideline criterion that the patient does NOT satisfy, with justification.
 
## Uncertain or Unverifiable Criteria
List criteria that could not be assessed due to missing data.
 
## Assessment
Based on the above, provide your overall assessment:
- Recommendation: SWITCH APPROVED / SWITCH NOT RECOMMENDED / INSUFFICIENT DATA
- Confidence: LOW / MODERATE / HIGH
- Clinical rationale: 2-3 sentences summarizing the key factors driving your recommendation.
 
Be objective. Base your assessment strictly on the evidence provided.
Do not introduce clinical knowledge beyond what is present in the investigation report."""

def exec_decision_maker(patient_summary: str, investigation_report: str) -> str:
    """
    Execute the Decision Maker agent to produce a clinical assessment based on the patient summary and investigation report.
    """
    
    messages = [
        SystemMessage(content=SYSTEM_PROMPT),
        HumanMessage(content=f"""## Patient Clinical Summary
 
    {patient_summary}
    
    ## Investigation Report (Guideline Criteria)
    
    {investigation_report}
    
    Please provide your structured clinical assessment for IV-to-oral antibiotic switch."""),
    ]
    
    response = llm_decision_maker.invoke(messages)
    return response.content
    