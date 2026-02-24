from langchain_chroma import Chroma
from app.config import VECTOR_DB_DIR

class ContractRetriever:

    def __init__(self, embedding_model):
        self.vectorstore = Chroma(
            persist_directory=VECTOR_DB_DIR,
            embedding_function=embedding_model
        )

    def retrieve(self, query, k=5): 
        docs = self.vectorstore.similarity_search_with_score(query, k=k)
        results = []
        for doc, score in docs:
            results.append({
                "content": doc.page_content,
                "source": doc.metadata["source"],
                "page": doc.metadata["page"],
                "score": score
            })
        return results