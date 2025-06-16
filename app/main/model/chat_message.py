
from app.main.extensions import db
from app.main.model.dto.chat_history_data import RoleEnum, MessageType
from sqlalchemy import Enum as SqlEnum

class ChatMessage(db.Model):
    __tablename__ = 'chat_message'

    id_message = db.Column(db.Integer, primary_key=True, autoincrement=True)
    contents = db.Column(db.Text, nullable=False)
    role = db.Column(SqlEnum(RoleEnum), nullable=False)
    position = db.Column(db.Integer, nullable=False)
    message_type = db.Column(SqlEnum(MessageType), nullable=False)

    chat_id = db.Column(db.Integer, db.ForeignKey('chat.id_chat'), nullable=False)

    __table_args__ = (
        db.UniqueConstraint('chat_id', 'position', name='uq_chat_message_position'),
    )

    def __init__(self, chat_id, contents, role, position, message_type):
        self.chat_id = chat_id
        self.contents = contents
        self.role = role
        self.position = position
        self.message_type = message_type