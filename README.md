#  Smart Contract AI: Enterprise RAG Legal Assistant

![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.104.1-009688.svg)
![LangChain](https://img.shields.io/badge/LangChain-Integration-green.svg)
![Gradio](https://img.shields.io/badge/Gradio-UI-orange.svg)
![ChromaDB](https://img.shields.io/badge/Chroma-Vector_DB-purple.svg)

##  Overview
The **Smart Contract AI** is an advanced Retrieval-Augmented Generation (RAG) pipeline specifically engineered for the legal domain. It allows users to upload complex legal contracts (PDF/DOCX) and ask context-specific questions. 

Unlike standard chatbots, this system is built with **strict guardrails against hallucinations**, ensuring that every generated answer is strictly grounded in the provided legal text, complete with source citations.

##  Key Features
* ** Multi-Format Document Ingestion:** Robust extraction from both `.pdf` and `.docx` files with automated chunking using `RecursiveCharacterTextSplitter`.
* ** High-Fidelity Vector Storage:** Local, secure embedding storage using **ChromaDB** and HuggingFace's `all-MiniLM-L6-v2` embedding model.
* ** Zero-Hallucination Guardrails:** Implements a strict `SIMILARITY_THRESHOLD` and engineered prompts. If the answer is not in the contract, the system explicitly states: *"Not found in document"*.
* ** Dual-Serving Architecture:** * Custom **FastAPI** endpoints for tailored front-end integration.
  * Standardized **LangServe** routes exposing LangChain Expression Language (LCEL) chains with built-in playgrounds.
* ** Contextual Memory:** Maintains a conversation state history (rolling window) to handle follow-up questions effectively.
* ** LLM-as-a-Judge Evaluation:** Features an automated evaluation pipeline inspired by the NVIDIA DLI framework, utilizing **DeepSeek R1** to score the RAG Triad (Context Relevance, Faithfulness, and Answer Relevance).
* ** Clean UI:** A modular, user-friendly interface built with **Gradio**, separating document indexing from the chat experience.

---

##  Technology Stack
* **Backend Framework:** FastAPI, LangServe
* **LLM Orchestration:** LangChain (LCEL)
* **LLM Provider:** OpenRouter API (Meta Llama 3 / DeepSeek R1 / Google Gemini)
* **Embeddings:** HuggingFace (`sentence-transformers/all-MiniLM-L6-v2`)
* **Vector Database:** ChromaDB (Local Storage)
* **Frontend UI:** Gradio
* **Data Parsing:** PyMuPDF (`fitz`), `python-docx`

---
##  Project Structure
```pash
smart-contract-assistant/
│
├── app/                        #  Core Application Modules
│   ├── __init__.py             
│   ├── config.py               # System configurations, thresholds, and ENV variables
│   ├── ingestion.py            # PDF/DOCX parsing, chunking, and embedding logic
│   ├── retriever.py            # ChromaDB interactions and semantic search
│   ├── llm_client.py           # OpenRouter API integration with real-time streaming
│   ├── rag_pipeline.py         # Main RAG orchestrator (Retrieval + Generation + Memory)
│   ├── api.py                  # FastAPI endpoints and LangServe LCEL chain integration
│   ├── gradio_app.py           # Gradio web interface (Frontend)
│   └── evaluate_judge.py       # DeepSeek R1 LLM-as-a-Judge evaluation script
│
├── data/
│   └── vector_db/              #  Local ChromaDB persistent storage (Auto-managed)
│
├── .env                        #  Secret keys and model endpoints (Not tracked in Git)
├── requirements.txt            #  Python dependencies
├── Contract.pdf                #  Sample legal document used for testing
├── Evaluation_Report.md        #  Detailed methodology and limitations report
├── NVIDIA_RAG_Evaluation_Report.csv #  Generated evaluation scores and LLM reasoning
└── README.md                   #  Main project documentation
```
------------------------------------------------------------------------

##  Technology Stack

Backend: - FastAPI - LangServe - LangChain (LCEL)

LLM Provider: - OpenRouter API - Meta Llama 3 - DeepSeek R1 - Google
Gemini

Embeddings: - HuggingFace all-MiniLM-L6-v2

Vector Database: - ChromaDB

Frontend: - Gradio

------------------------------------------------------------------------

#  Installation & Setup

## 1 Clone Repository
```pash
git clone https://github.com/yourusername/smart-contract-ai.git\
cd smart-contract-ai
```
## 2 Create Virtual Environment
```pash
python -m venv venv
```
Activate:
```pash
Windows: venv`\Scripts`{=tex}`\activate`{=tex}
```
```pash
Mac/Linux: source venv/bin/activate
```
## 3 Install Dependencies
```pash
pip install -r requirements.txt\
pip install sse_starlette
```
## 4 Configure Environment Variables

Create .env file:

OPENROUTER_API_KEY=your_openrouter_api_key_here\
OPENROUTER_MODEL=meta-llama/llama-3.2-3b-instruct:free\
OPENROUTER_BASE_URL=https://openrouter.ai/api/v1

------------------------------------------------------------------------

#  Running the Application

## Step 1: Start Backend
```pash
uvicorn app.api:app --reload

API Docs: http://127.0.0.1:8000/docs

LangServe Playground: http://127.0.0.1:8000/rag/playground/
```
## Step 2: Start Frontend
```pash
python app/gradio_app.py

Gradio UI: http://127.0.0.1:7860
```
------------------------------------------------------------------------

#  API Endpoints
```pash
/upload --- POST --- Upload + chunk + embed\
/ask_stream --- POST --- Streaming answers\
/rag/invoke --- POST --- LCEL invoke\
/rag/stream --- POST --- LCEL stream
```
------------------------------------------------------------------------

#  Author

Mohamed Ramadan\
AI Engineer\
Specialized in NLP, Computer Vision, and Generative AI
