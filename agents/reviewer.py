from langchain_core.messages import SystemMessage, HumanMessage
from config import llm_reviewer

# -------
# PROMPT 
# -------
# The Revisor is the adversarial agent, its explicit job is to find reasons
# why the switch should NOT happen.

SYSTEM_PROMPT = """You are a critical care pharmacist and patient safety specialist.
Your role is to act as a devil's advocate: actively search for reasons why
an IV-to-oral antibiotic switch should NOT be performed for this patient.

You will receive:
1. A clinical summary of the patient
2. An investigation report with criteria extracted from clinical guidelines

Your task is NOT to provide a balanced assessment. Your task is to:
- Identify every possible contraindication, risk factor, or red flag
- Challenge assumptions implicit in the patient data
- Flag missing information that could hide a contraindication
- Apply a safety-first lens: when in doubt, argue against the switch

Produce a structured report with the following sections:

## Contraindications Found
List any absolute or relative contraindications identified, with evidence.

## Red Flags and Risk Factors
List clinical findings that increase risk even if not absolute contraindications.

## Missing or Unreliable Data
List information gaps that could conceal a contraindication.
For each gap, explain what risk it represents.

## Safety Assessment
- Safety verdict: SWITCH UNSAFE / SWITCH RISKY / NO SAFETY CONCERNS FOUND
- Key concern: the single most important reason to be cautious (one sentence).

Be rigorous. Your job is to protect the patient from a premature switch.
If you find no safety concerns, say so explicitly — but only after exhausting
every possible line of questioning."""


def exec_reviewer(patient_summary: str, investigation_report: str) -> str:
    """
    Execute the Reviewer agent to identify any potential safety concerns or contraindications for switching from IV to oral antibiotic therapy based on the patient summary and investigation report.
    """
    
    messages = [
        SystemMessage(content=SYSTEM_PROMPT),
        HumanMessage(content=f"""## Patient Clinical Summary

    {patient_summary}

    ## Investigation Report (Guideline Criteria)

    {investigation_report}

    Identify every possible reason this patient should NOT be switched
    from IV to oral antibiotic therapy."""),
        ]

    response = llm_reviewer.invoke(messages)
    return response.content