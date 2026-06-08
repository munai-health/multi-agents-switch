from config_env import config_env
from langchain_core.tools import tool
from langchain_openai import OpenAIEmbeddings
from config import PINECONE_INDEX_NAME, PINECONE_TOP_K
from pinecone.grpc import PineconeGRPC
from llama_index.vector_stores.pinecone import PineconeVectorStore
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.core import Settings
from llama_index.core import VectorStoreIndex
from config_env import config_env

Settings.embed_model = OpenAIEmbedding(model="text-embedding-3-large", api_key=config_env.OPENAI_API_KEY)    
pinecone = PineconeGRPC(api_key=config_env.PINECONE_API_KEY)
pinecone_index = pinecone.Index(PINECONE_INDEX_NAME)
vector_store = PineconeVectorStore(pinecone_index=pinecone_index)
index = VectorStoreIndex.from_vector_store(vector_store)
retriever = index.as_retriever(similarity_top_k=3)

@tool
def search_criteria(query: str) -> str:
    """
    Search for clinical criteria for switching from IV to oral administration in medical guidelines.
    Use this to look up: eligiblity criteria, contraindications, clinical parameters (fever, white blood cell count,
    oral administration), specificic conditions (endocarditis, meningitis, osteomyelitis) and guidelines by antibiotic type.

    Return relevant excerpts from the guidelines with the source of each excerpt.

    Args:
        query: Specific clinical query in natural language
            Example: "What are the criteria for hemodynamic stability for an oral switch?"

    """

    docs = retriever.retrieve(query)

    if not docs:
        return "No relevant information found in the guidelines for the given query."

    results = []
    for i, doc in enumerate(docs):
        source = f"{doc.metadata.get('custom_title')} (Page {doc.metadata.get('page_number')})"
        results.append(f"Source: {source}\nExcerpt: {doc.text}...")

    return "\n\n---\n\n".join(results)
