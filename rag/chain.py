from langchain.chains import RetrievalQA
from langchain_ollama import OllamaLLM
from .retriever import get_retriever

def build_chain():
    retriever = get_retriever()
    
    llm = OllamaLLM(model="llama3.2")  # change to your ollama model name
    
    qa_chain = RetrievalQA.from_chain_type(
        llm=llm,
        retriever=retriever,
        chain_type="stuff",
        return_source_documents=True
    )
    return qa_chain
