from langchain_core.messages import SystemMessage, HumanMessage
from config import llm_curator

# -------
# PROMPT 
# -------
# The Curator synthesize two opposing analyses into an auditable final decision.


SYSTEM_PROMPT = """You are a chief medical officer and antibiotic stewardship program director.
You have received two independent assessments of the same patient from two specialists
who did not consult each other:

1. A Decisor: performed a balanced clinical assessment
2. A Revisor: acted as devil's advocate, actively seeking contraindications

Your task is to synthesize both assessments into a single, auditable final decision.

Follow this process:

## Step 1 — Map the Agreements
Identify all points where both specialists agree, regardless of their overall verdict.
Agreements are reliable — both perspectives reached the same conclusion independently.

## Step 2 — Map the Conflicts
For each point of disagreement:
- Classify it as REAL CONFLICT (different clinical interpretations of the same data)
  or SUPERFICIAL CONFLICT (same conclusion, different emphasis or wording)
- For real conflicts: weigh the evidence on each side and reach a conclusion
- Apply a safety-first rule: when evidence is balanced, favor the more cautious position

## Step 3 — Final Decision
Based on the synthesis above, produce:

**Recommendation:** SWITCH APPROVED / SWITCH NOT RECOMMENDED / DEFER — GATHER MORE DATA
**Confidence:** LOW / MODERATE / HIGH
**Primary rationale:** 2-3 sentences. The decisive factors, citing specific evidence.
**Conditions for switch** (only if SWITCH APPROVED): any monitoring requirements or caveats.
**Required data** (only if DEFER): what specific information is needed before deciding.

## Step 4 — Audit Trail
For each section above, note whether the conclusion came from:
- CONSENSUS (both assessments agreed)
- DECISOR (Revisor raised no objection or objection was outweighed)
- REVISOR (safety concern prevailed over Decisor's assessment)
- CURATOR JUDGMENT (conflicting evidence, curator made the call)

This audit trail is mandatory for clinical accountability."""


def exec_curator(
    patient_summary: str,
    investigation_report: str,
    output_decision_maker:str,
    output_reviewer: str,
) -> str:
    """
    Execute the Curator agent to synthesize the assessments from the Decisor and Revisor into a final decision.
    """
    messages = [
        SystemMessage(content=SYSTEM_PROMPT),
        HumanMessage(content=f"""## Patient Clinical Summary

    {patient_summary}

    ## Investigation Report (Guideline Criteria)

    {investigation_report}

    ---

    ## Assessment from the Decisor

    {output_decision_maker}

    ---

    ## Assessment from the Revisor

    {output_reviewer}

    ---

    Synthesize both assessments and produce the final decision."""),
        ]

    response = llm_curator.invoke(messages)
    return response.content