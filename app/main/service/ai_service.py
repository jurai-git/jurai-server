from typing import List

from flask_sqlalchemy import SQLAlchemy

from models.rag.retrieval_entry import RetrievalEntry
from models.rag.retriever import Retriever

class AIService:

    def __init__(self, db: SQLAlchemy, retriever: Retriever):
        self.db = db
        self.retriever = retriever

    def semantic_search(self, search: str) -> List[RetrievalEntry]:
        return self.retriever.semantic_search(search)

