from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from langchain_huggingface import HuggingFaceEmbeddings
from app.rag_pipeline import RAGPipeline
from app.ingestion import DocumentIngestor
import json
from typing import List, Dict, Any
import os
import shutil
from app.config import VECTOR_DB_DIR, OPENROUTER_API_KEY, OPENROUTER_MODEL, OPENROUTER_BASE_URL

# Clean the old database on startup
if os.path.exists(VECTOR_DB_DIR):
    print(f"🧹 Cleaning up old database at '{VECTOR_DB_DIR}'...")
    try:
        shutil.rmtree(VECTOR_DB_DIR)
        print("✨ Database cleared! Starting fresh.")
    except Exception as e:
        print(f"⚠️ Could not clear database: {e}")
else:
    print("✨ No old database found. Starting fresh.")


app = FastAPI(
    title="Smart Contract Q&A Assistant",
    version="1.0",
    description="A RAG pipeline API using FastAPI and LangServe"
)

# Download the model once at startup to avoid latency on first request
print(" Loading Embedding Model...")
shared_embedding_model = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)
print(" Model Loaded.")

pipeline = RAGPipeline(embedding_model=shared_embedding_model)
ingestor = DocumentIngestor(embedding_model=shared_embedding_model)

# 1. Custom Endpoints (for the Gradio interface)

class ChatRequest(BaseModel):
    question: str
    history: List[Dict[str, str]] = []

@app.post("/ask_stream")
def ask_stream(req: ChatRequest):
    answer_generator, sources = pipeline.answer_stream(req.question, req.history)
    def stream_response():
        yield json.dumps({"sources": sources}) + "\n"
        for chunk in answer_generator:
            yield chunk
    return StreamingResponse(stream_response(), media_type="text/plain")

@app.post("/upload")
def upload(file_path: str):
    try:
        count = ingestor.ingest(file_path)
        return {"chunks_indexed": count}
    except Exception as e:
        return {"error": str(e)}

# 2. LangServe Integration (Project Requirement)

from langserve import add_routes
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from pydantic import BaseModel 

# Preparing the model using the standard LangChain method
langchain_llm = ChatOpenAI(
    api_key=OPENROUTER_API_KEY,
    base_url=OPENROUTER_BASE_URL,
    model=OPENROUTER_MODEL
)

# Define the input format explicitly to solve the root problem
class RagInput(BaseModel):
    question: str

# An argument function to retrieve context from our Retriever
def get_context(input_dict: dict):
    question = input_dict["question"]
    docs = pipeline.retriever.retrieve(question)
    if not docs:
        return "No context found."
    return "\n\n".join([f"[Page {d['page']}]: {d['content']}" for d in docs])

# Building Prompt and Chain for LangServe
rag_prompt = ChatPromptTemplate.from_template("""
You are an expert Legal AI Assistant. Answer the question based ONLY on the following context.
If the answer is not in the context, say "Not found in document".

Context:
{context}

Question: {question}
""")

# Building an LCEL chain with input type specified to solve the Playground issue
rag_chain = (
    RunnablePassthrough()
    | {
        "context": get_context, 
        "question": lambda x: x["question"]
    }
    | rag_prompt
    | langchain_llm
    | StrOutputParser()
).with_types(input_type=RagInput) 

# Adding LangServe Paths
add_routes(
    app,
    rag_chain,
    path="/rag"
)

print(" LangServe routes added at /rag")