from typing import List

from app.main.extensions import db
from app.main.model.chat_message import ChatMessage


class Chat(db.Model):
    __tablename__ = 'chat'
    
    id_chat = db.Column(db.Integer, primary_key=True, autoincrement=True)
    messages = db.relationship('ChatMessage', backref='chat', lazy='dynamic')
    message_count = db.Column(db.Integer, nullable=False, default=0)

    demanda_id = db.Column(db.Integer, db.ForeignKey('demanda.id_demanda'))