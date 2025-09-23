from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings

CHROMA_DB_DIR = "chroma_db"

def get_retriever():
    embedding = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

    vectordb = Chroma(
        persist_directory=CHROMA_DB_DIR,
        embedding_function=embedding
    )

    retriever = vectordb.as_retriever(search_type="similarity", search_kwargs={"k": 5})
    return retriever
