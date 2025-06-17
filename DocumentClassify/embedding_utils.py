import os
from sentence_transformers import SentenceTransformer
from pinecone import Pinecone, ServerlessSpec
 
# Use your Pinecone API Key
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY", "pcsk_2hN28V_7qeN16ReybKNgr6qFXKw3rX8sgrJmiQatPNHLnJofxqzZQzbUY5PAd315jmC2ev")
INDEX_NAME = "gen-index"
EMBED_DIM = 384  # Match the sentence-transformer output dim
 
# Initialize Pinecone
pc = Pinecone(api_key=PINECONE_API_KEY)
 
# Create index if not exists
if INDEX_NAME not in pc.list_indexes().names():
    pc.create_index(
        name=INDEX_NAME,
        dimension=EMBED_DIM,
        metric="cosine",
        spec=ServerlessSpec(cloud="aws", region="us-west-2")
    )
 
# Connect to the index
index = pc.Index(INDEX_NAME)
 
# Load SentenceTransformer model
model = SentenceTransformer("all-MiniLM-L6-v2")
 
 
def get_embedding(text):
    return model.encode(text).tolist()
 
 
def add_document_to_pinecone(doc_id, text, metadata):
    embedding = get_embedding(text)
    index.upsert([(doc_id, embedding, metadata)])
 
 
def classify_document(text, top_k=3):
    embedding = get_embedding(text)
    return index.query(vector=embedding, top_k=top_k, include_metadata=True)
 