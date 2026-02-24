from app.retriever import ContractRetriever
from app.llm_client import OpenRouterClient
from app.config import SIMILARITY_THRESHOLD

class RAGPipeline:

    def __init__(self, embedding_model):
        self.retriever = ContractRetriever(embedding_model)
        self.llm = OpenRouterClient()

    def format_history(self, history):
        formatted = ""
        for msg in history[-5:]: 
            role = "User" if msg["role"] == "user" else "Assistant"
            formatted += f"{role}: {msg['content']}\n"
        return formatted

    def answer_stream(self, question, history):
        print("\n" + "="*60)
        print(f" [1] New Question Received: '{question}'")
        print(" [2] Searching Vector Database...")

        docs = self.retriever.retrieve(question)

       
        print(f" [3] Retrieval Complete. Found {len(docs)} chunks.")
        if docs:
            print(" --- Retrieved Chunks Details ---")
            for i, doc in enumerate(docs):
                print(f"   ➤ Chunk {i+1} | Score: {doc['score']:.4f} | Page: {doc['page']} | Source: {doc['source']}")
            print("----------------------------------")

        if not docs:
            print(" [4] No documents found in database. Aborting.")
            def empty_gen(): yield "No documents found. Please upload a file first."
            return empty_gen(), []

        best_score = min(doc["score"] for doc in docs)
        
        if best_score > SIMILARITY_THRESHOLD:
            print(f" [4] Best Score ({best_score:.4f}) is WORSE than Threshold ({SIMILARITY_THRESHOLD}).")
            print(" Conclusion: The retrieved text is irrelevant. Telling user 'Not found'.")
            def not_found_gen(): yield "I couldn't find specific information about that in the document."
            return not_found_gen(), []
        else:
            print(f" [4] Best Score ({best_score:.4f}) passed the Threshold ({SIMILARITY_THRESHOLD}). Relevant info found!")

        
        context_text = "\n\n".join([f"[Page {d['page']}]: {d['content']}" for d in docs])
        history_text = self.format_history(history)

        system_prompt = f"""You are an expert Legal AI Assistant. 
        Use the following Context to answer the User's Question.
        
        Rules:
        1. Answer ONLY based on the Context.
        2. If the answer is not in the Context, say "Not found in document".
        3. Consider the Chat History for context.
        
        Context:
        {context_text}
        """

        messages = [
            {"role": "system", "content": system_prompt},
        ]
        
        if history_text:
             messages.append({"role": "system", "content": f"Chat History:\n{history_text}"})

        messages.append({"role": "user", "content": question})

        print(" [5] Sending Prompt and Context to LLM via OpenRouter...")
        print(" [6] Waiting for stream response...")

        return self.llm.generate_stream(messages), docs