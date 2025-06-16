from app.main.extensions import db

class RagData(db.Model):
    __tablename__ = 'rag_data'

    id_rag = db.Column(db.Integer, primary_key=True, autoincrement=True)
    data = db.Column(db.Text, nullable=False)
    position = db.Column(db.Integer, nullable=False)

    chat_id = db.Column(db.Integer, db.ForeignKey('chat.id_chat'), nullable=False)

    __table_args__ = (
        db.UniqueConstraint('chat_id', 'position', name='uq_rag_data_position'),
    )

    def __init__(self, data, position):
        self.data = data
        self.position = position
