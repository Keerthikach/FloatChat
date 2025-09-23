from rag.chain import build_chain

def run_chat():
    qa_chain = build_chain()
    
    while True:
        query = input("You: ")
        if query.lower() in ["exit", "quit"]:
            break
        
        result = qa_chain.invoke({"query": query})
        print("\nAssistant:", result["result"])
        
        print("\n--- Sources ---")
        for doc in result["source_documents"]:
            print(doc.metadata)

if __name__ == "__main__":
    run_chat()
