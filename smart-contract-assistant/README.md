#  Smart Contract AI

### Enterprise-Grade RAG Legal Assistant

------------------------------------------------------------------------

##  Overview

Smart Contract AI is a production-ready Retrieval-Augmented Generation
(RAG) system engineered specifically for the legal domain.

It enables users to: - Upload complex legal contracts (.pdf / .docx) -
Ask clause-level, context-specific questions - Receive strictly grounded
answers with source citations

Unlike generic chatbots, this system enforces Zero-Hallucination
Guardrails, ensuring that responses are always derived from the uploaded
contract --- or explicitly state:

"Not found in document."

------------------------------------------------------------------------

##  Core Capabilities

###  Multi-Format Document Ingestion

-   Supports PDF via PyMuPDF (fitz)
-   Supports DOCX via python-docx
-   Intelligent chunking using RecursiveCharacterTextSplitter

###  High-Fidelity Vector Storage

-   Embeddings: sentence-transformers/all-MiniLM-L6-v2
-   Local persistent storage using ChromaDB
-   Automatic vector reset on startup

###  Zero-Hallucination Architecture

-   Strict SIMILARITY_THRESHOLD
-   Prompt-based refusal mechanism
-   Guaranteed contract-grounded outputs

###  Dual Serving Architecture

1.  Custom FastAPI endpoints (streaming + memory + citations)
2.  LangServe integration (LCEL chains + playground)

### 🧠 Contextual Conversation Memory

-   Rolling window memory
-   Handles follow-up queries effectively

###  LLM-as-a-Judge Evaluation

Automated evaluation inspired by NVIDIA RAG framework using DeepSeek R1.

Metrics: - Context Relevance - Faithfulness - Answer Relevance

Generates: NVIDIA_RAG_Evaluation_Report.csv

------------------------------------------------------------------------

##  Project Structure

project_root/ │ ├── app/ │ ├── config.py │ ├── ingestion.py │ ├──
retriever.py │ ├── llm_client.py │ ├── rag_pipeline.py │ ├── api.py │
├── gradio_app.py │ └── evaluate_judge.py │ ├── data/vector_db/ ├── .env
├── requirements.txt └── README.md

------------------------------------------------------------------------

## 🛠 Technology Stack

Backend: - FastAPI - LangServe - LangChain (LCEL)

LLM Provider: - OpenRouter API - Meta Llama 3 - DeepSeek R1 - Google
Gemini

Embeddings: - HuggingFace all-MiniLM-L6-v2

Vector Database: - ChromaDB

Frontend: - Gradio

------------------------------------------------------------------------

#  Installation & Setup

## 1 Clone Repository

git clone https://github.com/yourusername/smart-contract-ai.git\
cd smart-contract-ai

## 2 Create Virtual Environment

python -m venv venv

Activate:

Windows: venv`\Scripts`{=tex}`\activate`{=tex}

Mac/Linux: source venv/bin/activate

## 3 Install Dependencies

pip install -r requirements.txt\
pip install sse_starlette

## 4 Configure Environment Variables

Create .env file:

OPENROUTER_API_KEY=your_openrouter_api_key_here\
OPENROUTER_MODEL=meta-llama/llama-3.2-3b-instruct:free\
OPENROUTER_BASE_URL=https://openrouter.ai/api/v1

------------------------------------------------------------------------

#  Running the Application

## Step 1: Start Backend

uvicorn app.api:app --reload

API Docs: http://127.0.0.1:8000/docs

LangServe Playground: http://127.0.0.1:8000/rag/playground/

## Step 2: Start Frontend

python app/gradio_app.py

Gradio UI: http://127.0.0.1:7860

------------------------------------------------------------------------

#  API Endpoints

/upload --- POST --- Upload + chunk + embed\
/ask_stream --- POST --- Streaming answers\
/rag/invoke --- POST --- LCEL invoke\
/rag/stream --- POST --- LCEL stream

------------------------------------------------------------------------

#  Author

Mohamed Ramadan Mahgoub\
AI Engineer\
Specialized in NLP, Computer Vision, and Generative AI
