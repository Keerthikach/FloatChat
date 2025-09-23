import chromadb
from sentence_transformers import SentenceTransformer

# Initialize ChromaDB client and collection
client = chromadb.PersistentClient(path="./chroma_db")
collection = client.get_or_create_collection(name="argo_profiles")

# Initialize embeddings model
model = SentenceTransformer("all-MiniLM-L6-v2")

def sanitize_metadata(metadata):
    """
    Sanitize metadata for ChromaDB:
    - Replace None values with safe defaults
    - Convert lists (e.g., variables, depth_range) into strings
    """
    sanitized = {}
    for k, v in metadata.items():
        if v is None:
            if k in ["lat", "lon"]:
                sanitized[k] = 0.0
            elif k == "depth_range":
                sanitized[k] = "0,0"
            else:
                sanitized[k] = ""
        elif isinstance(v, list):
            # Convert list to a comma-separated string
            sanitized[k] = ",".join(map(str, v))
        else:
            sanitized[k] = v
    return sanitized

def save_to_chroma_batch(ids, vectors, metadatas):
    """
    Inserts embeddings and metadata into ChromaDB safely.
    - Ensures no None values
    - Converts lists to strings
    """
    if not ids or not vectors or not metadatas:
        print("No data to insert into ChromaDB.")
        return

    # Ensure all lengths match
    min_len = min(len(ids), len(vectors), len(metadatas))
    ids = ids[:min_len]
    vectors = vectors[:min_len]
    metadatas = [sanitize_metadata(m) for m in metadatas[:min_len]]

    try:
        collection.add(
            ids=ids,
            embeddings=vectors,
            metadatas=metadatas
        )
        print(f"Inserted {len(ids)} embeddings into ChromaDB successfully.")
    except Exception as e:
        print(f"❌ Error inserting into ChromaDB: {e}")
