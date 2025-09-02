import traceback
from typing import List, Tuple

from flask_sqlalchemy import SQLAlchemy
from flask.wrappers import Response
from flask import current_app, jsonify

from app.main.model.chat import Chat
from app.main.model.dto.semantic_search_dto import SemanticSearchDTO
from models.rag.llm.gemini_client import GeminiClient, GeminiContext
from models.rag.retrieval_entry import RetrievalEntry
from models.rag.retriever import Retriever
from google.genai.types import Content, Part


def _append_rag_data_or_error(chat: Chat, data: List[GeminiContext], chat_service) -> Chat | Tuple[Response, int]:
    try:
        stringified_data = GeminiClient.contexts_to_prompt(data)
        return chat_service.append_rag_data(chat, stringified_data)
    except Exception as e:
        traceback.print_exception(e)
        current_app.logger.error(f"Failed to append RAG msg to chat, returning error: {e}")
        return jsonify({
            'status': 'error',
            'message': 'INTERNAL_SERVER_ERROR',
            'details': 'Failed to persist RAG data to message list, unable to continue'
        }), 500


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

        gemini_contexts: List[GeminiContext] = self._postprocess_rag(semantic_search_results, ementa_relevances)

        return jsonify({
            "status": "SUCCESS",
            "response": self.gemini_client.generate_answer_from_context(query, gemini_contexts)
        }), 200

    def generate_answer_with_history_or_error(self, query: str, wants_rag: bool, id_demanda: int) -> str | tuple[Response, int]:
        with current_app.app_context():
            chat_service = current_app.extensions['chat_service']
            processo_service = current_app.extensions['processo_service']

            # get chat and append user's message
            chat: Chat = chat_service.get_or_create_chat(id_demanda)
            destructured_chat = chat_service.destructure_data(chat)
            if wants_rag:
                print("Adding rag")
                result = self._add_additional_rag(chat, destructured_chat, query, processo_service, chat_service)
                if type(result) == tuple:
                    return result

            chat = self._append_user_message_or_error(chat, query, chat_service)
            if type(chat) == tuple:
                return chat

            destructured_chat.append(
                Content(
                    role="user",
                    parts=[Part(text=query)]
                )
            )

            # finally, generate and persist the answer
            answer = self.gemini_client.generate_answer_with_history(destructured_chat)
            chat = self._append_model_message_or_error(chat, answer, chat_service)
            if type(chat) == tuple:
                return chat

            return answer

    def _add_additional_rag(self,
                                chat: Chat,
                                destructured_chat: List[Content],
                                query: str,
                                processo_service,
                                chat_service
                            ) -> None | Tuple[Response, int]:
        # generate rag data
        refined_query = self.refine_query(query)
        rag = self._retrieve_or_return_error(refined_query, processo_service)
        if type(rag) == tuple:
            return rag

        # postprocessing
        ementa_relevances = self.evaluate_ementa_relevances([context.ementa for context in rag], query)
        context_from_rag = self._postprocess_rag(rag, ementa_relevances)

        # add the rag result to the history, both in the DB and in the destructured data array
        chat = _append_rag_data_or_error(chat, context_from_rag, chat_service)
        if type(chat) == tuple:
            return chat

        # also append RAG to destructured chat
        destructured_chat.append(Content(
            role="user",
            parts=[Part(text=f"RAG_DATA: {context_from_rag}")]
        ))


    @staticmethod
    def _append_model_message_or_error(chat: Chat, message: str, chat_service):
        try:
            return chat_service.append_gemini_message(chat, message)
        except Exception as e:
            current_app.logger.error(f"Failed to append model msg to chat, returning error: {e}")
            return jsonify({
                'status': 'error',
                'message': 'INTERNAL_SERVER_ERROR',
                'details': 'Failed to persist model message to message list'
            }), 500

    @staticmethod
    def _append_user_message_or_error(chat: Chat, query: str, chat_service) -> Chat | Tuple[Response, int]:
        try:
            return chat_service.append_user_msg(chat, query)
        except Exception as e:
            current_app.logger.error(f"Failed to append user msg to chat, returning error: {e}")
            return jsonify({
                'status': 'error',
                'message': 'INTERNAL_SERVER_ERROR',
                'details': 'Failed to persist user message to message list'
            }), 500

    def _retrieve_or_return_error(self, query: str, processo_service) -> List[SemanticSearchDTO] | Tuple[Response, int]:
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

    def retrieve_or_return_error(self, query: str, processo_service) -> List[SemanticSearchDTO] | Tuple[Response, int]:
        with current_app.app_context():
            return self._retrieve_or_return_error(query, processo_service)

    @staticmethod
    def _postprocess_rag(semantic_search_results: List[SemanticSearchDTO], ementa_relevances: List[float]) -> List[GeminiContext]:
        gemini_contexts: List[GeminiContext] = []
        for i in range(len(ementa_relevances)):
            if ementa_relevances[i] < 0.25:
                continue
            gemini_contexts.append(GeminiContext(
                semantic_search_results[i],
                ementa_relevances[i],
            ))
        return gemini_contexts