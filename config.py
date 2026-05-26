from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic

from config_env import config_env

# -------
# MODELS 
# -------

# -- Investigator: Call Lucas Tool, and, uses the information to consult the vector store 
llm_investigator = ChatOpenAI(api_key=config_env.OPENAI_API_KEY, model="gpt-4o-mini", temperature = 0)

# -- Decision Maker: Takes the information from the investigator and makes an initial decision on what to do next
llm_decision_maker = ChatOpenAI(api_key=config_env.OPENAI_API_KEY, model="gpt-4o", temperature = 0.2)

# -- Reviewer: Takes the decision from the decision maker and reviews it, try to find reasons to not do the switch
llm_reviewer = ChatAnthropic(model="claude-sonnet-4-5", temperature = 0.2)

# -- Curator: Takes the decision from the decision maker and the review from the reviewer, and makes a final decision on what to do next
llm_curator = ChatOpenAI(api_key=config_env.OPENAI_API_KEY, model="gpt-4o", temperature = 0.1)

# -------
# Vector Store 
# -------

PINECONE_INDEX_NAME = "munai-guidelines-switch-chunk-per-pdf"
PINECONE_TOP_K = 5

# -------
# Extra Setup 
# -------
MAX_INVESTIGATOR_ITERATIONS = 10
