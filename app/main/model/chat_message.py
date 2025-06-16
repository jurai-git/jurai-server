
from app.main.extensions import db

class ChatMessage(db.Model):
    __tablename__ = 'chat_message'

    id_message = db.Column(db.Integer, primary_key=True, autoincrement=True)
    contents = db.Column(db.Text, nullable=False)
    role = db.Column(db.String(16), nullable=False)
    position = db.Column(db.Integer, nullable=False)

    chat_id = db.Column(db.Integer, db.ForeignKey('chat.id_chat'), nullable=False)

    __table_args__ = (
        db.UniqueConstraint('chat_id', 'position', name='uq_chat_message_position'),
    )

    def __init__(self, contents, role, position):
        self.contents = contents
        self.role = role
        self.position = position