# IV-to-Oral Antibiotic Switch Evaluator

A multi-agent clinical decision support system that evaluates whether hospitalized patients should switch from intravenous (IV) to oral antibiotic therapy. Given a FHIR encounter ID, the pipeline fetches patient data, queries clinical guidelines, and produces an auditable final recommendation.

## Overview

**Input:** A hospital encounter ID  
**Output:** A structured recommendation (`SWITCH APPROVED` / `NOT RECOMMENDED` / `DEFER — GATHER MORE DATA`) with full audit trail

---

## Architecture

### Pipeline (LangGraph)

```
summary → investigator → decision_maker ─┐
                       ↘                 ├→ curator → END
                         reviewer ───────┘
```

`decision_maker` and `reviewer` run in **parallel** after `investigator` completes. Both feed into `curator`, which produces the final decision.

State is carried through every node via `PipelineState`:

```python
class PipelineState(TypedDict):
    encounter_id: str           # Input: FHIR encounter ID
    patient_summary: str        # Output of summary agent
    investigation_report: str   # Output of investigator agent
    output_decision_maker: str  # Output of decision_maker agent
    output_reviewer: str        # Output of reviewer agent
    final_decision: str         # Output of curator agent (final recommendation)
```

### Agent Roles

| Agent | LLM | Temperature | Role |
|---|---|---|---|
| **summary** | GPT-4o | 0 | Converts raw FHIR data into a structured Portuguese clinical narrative |
| **investigator** | GPT-4o | 0 | ReAct loop: queries Pinecone guidelines until all mandatory topics are covered (max 10 iterations) |
| **decision_maker** | GPT-4o | 0.2 | Balanced assessment mapping criteria met/not met; issues verdict with confidence level |
| **reviewer** | Claude Sonnet 4.5 (AWS Bedrock) | 0.2 | Adversarial devil's advocate: actively searches for contraindications and safety concerns |
| **curator** | GPT-4o | 0.1 | Synthesizes both outputs; resolves conflicts; produces audit trail |

#### Why two different LLM providers?

`decision_maker` (GPT-4o) and `reviewer` (Claude Sonnet via Bedrock) intentionally use different models to avoid groupthink. The reviewer's adversarial safety role benefits from a model trained with different priors. Using separate providers ensures independent reasoning before the curator synthesizes both outputs.

### Curator Audit Trail

The curator annotates every conclusion with its source:

| Label | Meaning |
|---|---|
| `CONSENSUS` | Both decision_maker and reviewer agreed |
| `DECISOR` | Reviewer had no objection or was outweighed by evidence |
| `REVISOR` | Safety concern from reviewer prevailed |
| `CURATOR JUDGMENT` | Conflicting evidence; curator applied safety-first tie-breaking |

### Data Flow

1. `get_encounter_info(encounter_id)` sends two FHIR batch bundles to the server (primary: patient, conditions, encounter/locations, Munai Score observation, procedures; secondary: clinical impressions, antibiotic medication requests, Munai Score history).
2. `parse_encounter_data(raw)` — deterministic Python parser extracts structured fields. Lab values (CBC, CRP) remain inside free-text clinical notes for the LLM to extract.
3. `summarize_patient(parsed)` — GPT-4o produces a structured Portuguese markdown report. Windowed to last 7 clinical notes and last 5 Munai Score entries to stay within context limits.
4. `exec_investigator(summary)` — ReAct agent calls `search_criteria` (Pinecone tool) repeatedly until all mandatory topics are covered or 10 iterations are reached. Topics include: clinical stability criteria, oral route criteria, absolute contraindications, infection-type-specific criteria, lab parameters (WBC, CRP, procalcitonin), and vital sign parameters.
5. `exec_decision_maker` and `exec_reviewer` run in parallel on the same summary + investigation report.
6. `exec_curator` synthesizes both outputs into the final decision with audit trail.

### Infrastructure Layers

| Layer | File | Responsibility |
|---|---|---|
| HTTP client | `adapters/http_adapter.py` | Thin `httpx` wrapper for all outbound HTTP (POST only) |
| FHIR auth + data | `providers/fhir_provider.py` | Keycloak token lifecycle (client credentials + refresh rotation); FHIR Bundle POST |
| Guideline retrieval | `tools/pinecone_tool.py` | LangChain `@tool` wrapping a LlamaIndex retriever over the Pinecone index |
| Patient data parsing | `tools/fhir_parser.py` | Pure deterministic FHIR parser; no LLM; handles HTML-stripping, recursive location resolution, ICU detection |

### Pinecone Index

| Property | Value |
|---|---|
| Index name | `munai-guidelines-switch-chunk-per-md` |
| Embedding model | `text-embedding-3-large` (3072 dimensions) |
| Retrieval | Top-3 chunks per query (similarity search) |
| Infrastructure | AWS serverless, `us-east-1` |

---

## Clinical Guideline Sources

The Pinecone index is built from four authoritative documents:

| Document | Description |
|---|---|
| **WHO AWaRe Antibiotic Book** | WHO classification of antibiotics into Access, Watch, and Reserve categories; prescribing criteria and stewardship guidance |
| **ANVISA Antimicrobial Stewardship Guideline** | Brazilian national health surveillance agency guideline for rational antibiotic use in hospital settings |
| **UKHSA IVOS Decision Aid (Adult)** | UK Health Security Agency intravenous-to-oral antibiotic switch criteria for adult patients |
| **UKHSA IVOS Decision Aid (Paediatric)** | UK Health Security Agency intravenous-to-oral antibiotic switch criteria for paediatric patients |

---

## Setup

### Prerequisites

- Python **3.11** (exactly; 3.12+ is not supported due to dependency constraints)
- [Poetry](https://python-poetry.org/)

### Install dependencies

```bash
poetry install
```

### Configure environment variables

Create a `.env` file in the project root:

```env
# OpenAI — used by summary, investigator, decision_maker, curator agents
OPENAI_API_KEY=sk-...

# Pinecone — vector store for clinical guidelines
PINECONE_API_KEY=pcsk_...

# AWS Bedrock — used by the reviewer agent (Claude Sonnet)
AWS_ACCESS_KEY_ID=ASIA...
AWS_SECRET_ACCESS_KEY=...
AWS_SESSION_TOKEN=...   # Only required for temporary IAM role credentials

# Keycloak — OAuth2 authentication for the FHIR server
KEYCLOAK_URL=https://<sso-host>
KEYCLOAK_REALM_ID=<realm>
KEYCLOAK_CLIENT_ID=<client-id>
KEYCLOAK_CLIENT_SECRET=<client-secret>

# FHIR server
FHIR_URL=https://<fhir-host>/fhir
FHIR_PARTITION=<partition>
```

| Variable | Description |
|---|---|
| `OPENAI_API_KEY` | GPT-4o API key for all agents except the reviewer |
| `PINECONE_API_KEY` | API key for the Pinecone guideline vector store |
| `AWS_ACCESS_KEY_ID` | AWS credentials for Bedrock (reviewer agent) |
| `AWS_SECRET_ACCESS_KEY` | AWS secret key |
| `AWS_SESSION_TOKEN` | Temporary session token for IAM role assumption (omit for long-term credentials) |
| `KEYCLOAK_URL` | Base URL of the Keycloak SSO server |
| `KEYCLOAK_REALM_ID` | Keycloak realm name |
| `KEYCLOAK_CLIENT_ID` | OAuth2 client ID |
| `KEYCLOAK_CLIENT_SECRET` | OAuth2 client secret |
| `FHIR_URL` | FHIR server base URL |
| `FHIR_PARTITION` | FHIR tenant/partition identifier |

---

## Running the Pipeline

```bash
python main.py <encounter_id>
```

The pipeline returns a dict with all intermediate and final outputs:

| Field | Content |
|---|---|
| `patient_summary` | Structured Portuguese clinical narrative (demographics, vitals, labs, medications, Munai Score history) |
| `investigation_report` | Guideline evidence gathered by the investigator (criteria for and against switch, sources) |
| `output_decision_maker` | Balanced assessment with criteria met/not met and verdict |
| `output_reviewer` | Adversarial safety report with contraindications and red flags |
| `final_decision` | Curator synthesis with audit trail and final recommendation |

---

## One-Time Setup: Ingest Guidelines into Pinecone

Before first use, populate the Pinecone index with the clinical guideline PDFs:

1. Place the source PDFs in `./Docs/`
2. Run:

```bash
python upsert_chunks.py
```

This ingests the documents using semantic chunking (LlamaIndex `SemanticSplitterNodeParser`), embeds them with `text-embedding-3-large`, and upserts the vectors into the `munai-guidelines-switch-chunk-per-md` index (AWS serverless, `us-east-1`, 3072 dimensions). The script is idempotent — it skips index creation if the index already exists.

---

## Technology Stack

| Component | Technology |
|---|---|
| Workflow orchestration | [LangGraph](https://langchain-ai.github.io/langgraph/) |
| LLM abstraction | [LangChain](https://python.langchain.com/) |
| Primary LLM | GPT-4o (OpenAI) |
| Reviewer LLM | Claude Sonnet 4.5 (AWS Bedrock via `langchain-aws`) |
| Vector store | [Pinecone](https://www.pinecone.io/) (gRPC client) |
| RAG framework | [LlamaIndex](https://www.llamaindex.ai/) |
| Patient data | FHIR R4 (HL7) |
| Authentication | Keycloak (OAuth2 client credentials) |
| HTTP client | [httpx](https://www.python-httpx.org/) |
| Config management | [pydantic-settings](https://docs.pydantic.dev/latest/concepts/pydantic_settings/) |
| Dependency management | [Poetry](https://python-poetry.org/) |
| Python version | 3.11 |
