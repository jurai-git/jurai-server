# if this is imported, it means the app was started with use_ai=True
import os

from models.rag.llm.gemini_client import GeminiClient
from models.rag.retriever import Retriever

gemini_api_key = os.getenv('GEMINI_API_KEY')
pinecone_api_key = os.getenv('PINECONE_API_KEY')
pinecone_index_url = os.getenv('PINECONE_INDEX_URL')

retriever: Retriever = Retriever(pinecone_api_key, pinecone_index_url)
gemini_client: GeminiClient = GeminiClient(gemini_api_key)