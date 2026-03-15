import chromadb
import os

# Ensure storage directory exists
os.makedirs("./chroma_db", exist_ok=True)

# Persistent client — saves to disk between sessions
client = chromadb.PersistentClient(path="./chroma_db")

# Collection for storing past email generations
collection = client.get_or_create_collection(
    name="email_memory",
    metadata={"hnsw:space": "cosine"}  # Cosine similarity for text matching
)