import chromadb
import os
from chromadb.utils.embedding_functions import DefaultEmbeddingFunction

os.makedirs("./chroma_db", exist_ok=True)

client = chromadb.PersistentClient(path="./chroma_db")

collection = client.get_or_create_collection(
    name="email_memory",
    metadata={"hnsw:space": "cosine"},
    embedding_function=DefaultEmbeddingFunction()
)