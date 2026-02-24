import os
from dotenv import load_dotenv

load_dotenv()

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
OPENROUTER_MODEL = os.getenv("OPENROUTER_MODEL")

# --- The edit here: We added this line because LangServe needs it and doesn't throw an error 
OPENROUTER_BASE_URL = os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1")

VECTOR_DB_DIR = "data/vector_db"
CHUNK_SIZE = 1000  
CHUNK_OVERLAP = 200
SIMILARITY_THRESHOLD = 2.5