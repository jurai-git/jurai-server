from typing import List, Tuple

from flask_sqlalchemy import SQLAlchemy
from flask.wrappers import Response
from flask import current_app, jsonify


from app.main.model.dto.semantic_search_dto import SemanticSearchDTO
from models.rag.llm.gemini_client import GeminiClient, GeminiContext
from models.rag.retrieval_entry import RetrievalEntry
from models.rag.retriever import Retriever

class AIService:

    def __init__(self, db: SQLAlchemy, retriever: Retriever, gemini_client: GeminiClient):
        self.db = db
        self.retriever = retriever
        self.gemini_client = gemini_client

    def semantic_search(self, search: str) -> List[RetrievalEntry]:
        return self.retriever.semantic_search(search, count=5)

    def refine_query(self, query: str) -> str:
        return self.gemini_client.rewrite_query_for_retrieval(query)

    def evaluate_ementa_relevances(self, ementas: List[str], query: str) -> List[float]:
        return self.gemini_client.rate_ementa_relevances(ementas, query)

    def generate_final_answer_or_error(self, query: str, semantic_search_results: List[SemanticSearchDTO]) -> str | tuple[Response, int]:
        ementa_relevances = self.evaluate_ementa_relevances([context.ementa for context in semantic_search_results], query)

        if len(ementa_relevances) != len(semantic_search_results) or len(ementa_relevances) == 0:
            current_app.logger.error("Ementa relevances and semantic search results weren't the same shape or were empty; returning internal error")
            return jsonify({
                'status': 'error',
                'message': 'INTERNAL_SERVER_ERROR',
                'details': 'One of our internal query preprocessing steps failed.'
            }), 500

        gemini_contexts: List[GeminiContext] = []
        for i in range(len(ementa_relevances)):
            if ementa_relevances[i] < 0.25:
                continue
            gemini_contexts.append(GeminiContext(
                semantic_search_results[i],
                ementa_relevances[i],
            ))

        return jsonify({
            "status": "SUCCESS",
            "response": self.gemini_client.generate_answer_from_context(query, gemini_contexts)
        }), 200

    def retrieve_or_return_error(self, query: str, processo_service) -> List[SemanticSearchDTO] | Tuple[Response, int]:
        with current_app.app_context():

            entries = self.semantic_search(query)
            processos = processo_service.get_all_by_num_tjmg([entry.numero_tjmg for entry in entries])

            if len(processos) == 0 or len(entries) == 0:
                return jsonify({
                    'status': 'error',
                    'message': 'ERROR_NO_ENTRIES_FOUND'
                }), 404

            if len(processos) != len(entries):
                return jsonify({
                    'status': 'error',
                    'message': 'INTEGRITY_ERROR'
                }), 500

            dtos: List[SemanticSearchDTO] = []
            for i, _ in enumerate(processos):
                dtos.append(SemanticSearchDTO(processos[i], entries[i].similarity))

            return dtos

