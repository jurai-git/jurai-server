from typing import List

from flask_sqlalchemy import SQLAlchemy

from app.main.model.chat import Chat
from app.main.model.chat_message import ChatMessage
from app.main.model.demanda import Demanda
from app.main.model.dto.chat_history_data import GeminiMessage, GeminiPart


class ChatService:

    def __init__(self, db: SQLAlchemy):
        self.db = db


    # TODO: Right now, we are assuming a 1:1 relationship between demanda and chat.
    # TODO: In the future, an advogado may have more than one chat per demanda. But, for now, this should work.
    def get_chat_by_demanda_id(self, demanda_id) -> Chat:
        chats = self.db.query(Chat).filter_by(demanda_id=demanda_id).all()
        if len(chats) == 0:
            return None
        return chats[0]

    def create_chat(self, demanda_id) -> Chat:
        chat = Chat()
        chat.demanda_id = demanda_id

        try:
            self.db.session.add(chat)
            self.db.session.commit()
        except Exception as e:
            self.db.session.rollback()
            raise e

        return chat

    def append_user_msg(self, chat: Chat, msg: str):
        pos = chat.message_count
        chat_msg = ChatMessage(chat.id_chat, msg, "user", pos, "default")

        self._persist_message(chat, chat_msg)

        return chat_msg

    def append_rag_data(self, chat: Chat, data: str):
        pos = chat.message_count
        chat_msg = ChatMessage(chat.id_chat, data, "user", pos, "rag")

        self._persist_message(chat, chat_msg)

        return chat_msg

    def append_gemini_message(self, chat: Chat, message: str):
        pos = chat.message_count
        chat_msg = ChatMessage(chat.id_chat, message, "model", pos, "default")

        self._persist_message(chat, chat_msg)

    def _persist_message(self, chat: Chat, message: ChatMessage):
        try:
            chat = self.db.session.merge(chat)
            self.db.session.add(message)
            chat.message_count += 1
            self.db.session.add(chat)
            self.db.session.commit()
        except Exception as e:
            self.db.session.rollback()
            raise e

    @staticmethod
    def destructure_data(chat: Chat) -> List[GeminiMessage]:
        temp: dict[int, ChatMessage] = {}

        for message in chat.messages.all():
            temp[message.position] = GeminiMessage({
                "role": message.role,
                "parts": [GeminiPart({
                    "text": f"[[RAG_DATA]]: {message.contents}" if message.type == "rag" else message.contents
                })],
            })

        print(temp)
        return [temp[pos] for pos in sorted(temp)]









