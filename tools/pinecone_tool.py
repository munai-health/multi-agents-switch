from langchain_core.tools import tool
from langchain_pinecone import PineconeVectorStore
from langchain_openai import OpenAIEmbeddings
from config import PINECONE_INDEX_NAME, PINECONE_TOP_K

embeddings = OpenAIEmbeddings(model="text-embedding-3-large")

vector_store = PineconeVectorStore(
    index_name = PINECONE_INDEX_NAME,
    embedding = embeddings
)

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
    
    docs = vector_store.similarity_search(query, k=PINECONE_TOP_K)
    
    if not docs:
        return "No relevant information found in the guidelines for the given query."
    
    results = []
    for i, doc in enumerate(docs):
        source = f"{doc.metadata.get('custom_title')} (Page {doc.metadata.get('page_number')})"
        results.append(f"Source: {source}\nExcerpt: {doc.text}...")
        
    return "\n\n---\n\n".join(results) 
        