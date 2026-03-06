import os
from typing import List, Dict
from llama_index.llms.openai import OpenAI
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.core.extractors import BaseExtractor
from pinecone.grpc import PineconeGRPC
from pinecone import ServerlessSpec
from llama_index.vector_stores.pinecone import PineconeVectorStore
from llama_index.core.ingestion.pipeline import IngestionPipeline
from pinecone.exceptions import PineconeApiException
from llama_index.core.node_parser import SemanticSplitterNodeParser
from llama_index.core import SimpleDirectoryReader

files_metadata = {
    "The WHO AWaRe antibiotic bookantibiotic book.pdf": 
        {
            "custom_title": "The WHO AWaRe antibiotic bookantibiotic book",
            "custom_link": "https://www.who.int/publications/i/item/9789240062382",
            "general_topic": "antibiotic book",
            "important_pages": [486, 605]
        },
    "Diretriz Nacional para Elaboração de Programa de Gerenciamento de Antimicrobianos em Serviços de Saúde.pdf":
        {
            "custom_title": "Diretriz Nacional para Elaboração de Programa de Gerenciamento de Antimicrobianos em Serviços de Saúde",
            "custom_link": "https://www.gov.br/anvisa/pt-br/centraisdeconteudo/publicacoes/servicosdesaude/publicacoes/DiretrizGerenciamentoAntimicrobianosANVISA2023FINAL.pdf",
            "general_topic": "national guideline for the development of antimicrobial stewardship programs in healthcare services.",
            "important_pages": [29]
        },
    "Antimicrobial Intravenous-to-Oral Switch (IVOS) Decision Aid.pdf":
        {
            "custom_title": "Antimicrobial Intravenous-to-Oral Switch (IVOS) Decision Aid",
            "custom_link": "https://assets.publishing.service.gov.uk/media/63da4c5de90e0773d99d59d0/Final_IV_to_Oral_Switch_Decision_Aid_based_on_NationalCriteria_UKHSA.pdf",
            "general_topic": "antimicrobial intravenous-to-oral switch (IVOS) decision aid",
            "important_pages": [1]
        },
    "Antimicrobial Intravenous-to-Oral Switch (IVOS) Decision Aid for paediatrics.pdf":
        {
            "custom_title": "Antimicrobial Intravenous-to-Oral Switch (IVOS) Decision Aid for paediatrics",
            "custom_link": "https://assets.publishing.service.gov.uk/media/66795c88a7a18c1aa1a00f20/paeds-iv-to-oral-switch-decision-aid-1.pdf",
            "general_topic": "antimicrobial intravenous-to-oral switch (IVOS) decision aid for paediatrics",
            "important_pages": [1]
        }
}

class CustomExtractor(BaseExtractor):
    def extract(self, nodes) -> List[Dict]:
        metadata_list = []
        for node in nodes:
            file_name = os.path.basename(node.metadata.get("file_name", ""))
            
            info = files_metadata.get(file_name, {
                "custom_title": "unknown",
                "custom_link": "N/A",
                "general_topic": "unknown"
            })
            
            metadata_list.append({
                "custom_title": info.get("custom_title"),
                "custom_link": info.get("custom_link"),
                "general_topic": info.get("general_topic"),
                "page_number": node.metadata.get("page_label") 
            })
        return metadata_list

PDF_DIR = "./Docs"
pinecone_api_key = os.environ['PINECONE_API_KEY']
embed_model = OpenAIEmbedding(model="text-embedding-3-large") 
llm = OpenAI(model="gpt-4-turbo")

semantic_parser = SemanticSplitterNodeParser(
   buffer_size=2, 
   breakpoint_percentile_threshold=95, 
   embed_model=embed_model
)

pc = PineconeGRPC(api_key=os.environ['PINECONE_API_KEY'])
index_name = "munai-guidelines-switch-chunk-per-pdf"

try:
   pc.create_index(
       index_name,
       dimension=3072,
       spec=ServerlessSpec(cloud="aws", region="us-east-1"),
   )
except PineconeApiException as e:
   if "ALREADY_EXISTS" in str(e):
       print(f"Index '{index_name}' already exists. Continuing with existing index.")
   else:
       raise

pinecone_index = pc.Index(index_name)
vector_store = PineconeVectorStore(pinecone_index=pinecone_index)

pipeline = IngestionPipeline(
   transformations=[
       semantic_parser,    
       CustomExtractor(),  
       embed_model,        
   ],
   vector_store=vector_store
)

all_docs = SimpleDirectoryReader(input_dir=PDF_DIR).load_data()
filtered_docs = []

for doc in all_docs:
    file_name = os.path.basename(doc.metadata.get("file_name", ""))
    
    try:
        page_num = int(doc.metadata.get("page_label", "0")) 
    except:
        continue
    
    if file_name in files_metadata:
        if page_num in files_metadata[file_name]["important_pages"]:
            filtered_docs.append(doc)

print(f"Num of documents after filtering: {len(filtered_docs)}")

nodes = pipeline.run(documents=filtered_docs)

print(f"Successfully processed and upserted {len(nodes)} nodes to Pinecone index '{index_name}'.")