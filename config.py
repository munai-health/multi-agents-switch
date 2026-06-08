from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain_aws import ChatBedrockConverse


from config_env import config_env

# -------
# MODELS 
# -------

# -- Summarizer: Takes the raw data from the FHIR parser and summarizes it into a concise report, highlighting the most relevant information for the switch decision
llm_summarizer = ChatOpenAI(api_key=config_env.OPENAI_API_KEY, model="gpt-4o", temperature = 0)

# -- Investigator: Consult the vector store to find relevant information in the guidelines, and gather evidence to support or contraindicate the switch.
llm_investigator = ChatOpenAI(api_key=config_env.OPENAI_API_KEY, model="gpt-4o", temperature = 0)

# -- Decision Maker: Takes the information from the investigator and makes an initial decision on what to do next
llm_decision_maker = ChatOpenAI(api_key=config_env.OPENAI_API_KEY, model="gpt-4o", temperature = 0.2)

# -- Reviewer: Takes the decision from the decision maker and reviews it, try to find reasons to not do the switch
llm_reviewer = ChatBedrockConverse(
    model="us.anthropic.claude-sonnet-4-5-20250929-v1:0",
    region_name="us-east-1",
    temperature=0.2,
    aws_access_key_id=config_env.AWS_ACCESS_KEY_ID,
    aws_secret_access_key=config_env.AWS_SECRET_ACCESS_KEY,
    aws_session_token=config_env.AWS_SESSION_TOKEN or None,
)


# -- Curator: Takes the decision from the decision maker and the review from the reviewer, and makes a final decision on what to do next
llm_curator = ChatOpenAI(api_key=config_env.OPENAI_API_KEY, model="gpt-4o", temperature = 0.1)

# -------
# Vector Store 
# -------

PINECONE_INDEX_NAME = "munai-guidelines-switch-chunk-per-md"
PINECONE_TOP_K = 5

# -------
# Extra Setup 
# -------
MAX_INVESTIGATOR_ITERATIONS = 10
