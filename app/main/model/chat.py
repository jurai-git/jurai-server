from app.main.extensions import db


class Chat(db.Model):
    __tablename__ = 'chat'
    
    id_chat = db.Column(db.Integer, primary_key=True, autoincrement=True)
    messages = db.relationship('ChatMessage', backref='chat', lazy='dynamic')
    message_count = db.Column(db.Integer, nullable=False, default=0)

    demanda_id = db.Column(db.Integer, db.ForeignKey('demanda.id_demanda'))

    def serialize_full(self):
        return {
            'id_chat': self.id_chat,
            'message_count': self.message_count,
            'messages': [
                message.serialize() for message in self.messages.all()
            ]
        }

    def serialize_streamlined(self):
        return {
            'id_chat': self.id_chat,
            'message_count': self.message_count,
        }