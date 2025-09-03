from typing import List

from flask_sqlalchemy import SQLAlchemy
from app.main.model.chat import Chat
from app.main.model.chat_message import ChatMessage
from google.genai.types import Content, Part
from sqlalchemy.orm.exc import NoResultFound

from app.main.model.demanda import Demanda
from app.main.model.requerente import Requerente


class ChatService:
    def __init__(self, db: SQLAlchemy):
        self.db = db

    # TODO: Right now, we are assuming a 1:1 relationship between demanda and chat.
    # TODO: In the future, an advogado may have more than one chat per demanda. But, for now, this should work.
    def get_chat_by_demanda_id(self, demanda_id) -> Chat | None:
        chats = (
            self.db.session.query(Chat)
            .join(Chat.demanda)
            .filter(
                Chat.demanda_id == demanda_id,
            )
            .all()
        )
        if len(chats) == 0:
            return None
        return chats[0]

    def get_chat_by_id_and_advogado(self, advogado, chat_id) -> Chat | None:
        try:
            chat = (
                self.db.session.query(Chat)
                .join(Chat.demanda)
                .join(Demanda.requerente)
                .filter(
                    Chat.id_chat == chat_id,
                    Requerente.advogado_id == advogado.id_advogado
                )
                .one()
            )
            return chat
        except NoResultFound:
            return None

    def get_all_from_advogado(self, advogado):
        chats = self.db.session.query(Chat).join(Demanda.requerente).filter(Requerente.advogado_id == advogado.id_advogado).all()

        return chats

    def get_or_create_chat(self, demanda_id) -> Chat:
        chat = self.get_chat_by_demanda_id(demanda_id)

        if chat is None:
            chat = Chat()
            chat.demanda_id = demanda_id
            try:
                self.db.session.add(chat)
                self.db.session.commit()
            except Exception as e:
                self.db.session.rollback()
                raise e

        return chat

    def append_user_msg(self, chat: Chat, msg: str) -> Chat:
        pos = chat.message_count
        chat_msg = ChatMessage(chat.id_chat, msg, "user", pos, "default")
        self._persist_message(chat, chat_msg)

        return chat

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
    def destructure_data(chat: Chat) -> List[Content]:
        temp: dict[int, Content] = {}

        for message in chat.messages.all():
            temp[message.position] = Content(
                    role=message.role,
                    parts=[Part(
                        text=f"RAG_DATA: {message.contents}" if message.message_type == "rag" else message.contents
                    )]
            )

        return [temp[pos] for pos in sorted(temp)]
