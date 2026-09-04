import os
from pathlib import Path
import chromadb
from chromadb.utils.embedding_functions import DefaultEmbeddingFunction

DB_DIR = Path(__file__).resolve().parent.parent / "chroma_db"
os.makedirs(DB_DIR, exist_ok=True)

client = chromadb.PersistentClient(path=str(DB_DIR))

collection = client.get_or_create_collection(
    name="email_memory",
    metadata={"hnsw:space": "cosine"},
    embedding_function=DefaultEmbeddingFunction()
)