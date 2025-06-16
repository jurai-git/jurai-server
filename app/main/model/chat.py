from app.main.extensions import db

class Chat(db.Model):
    __tablename__ = 'chat'
    
    id_chat = db.Column(db.Integer, primary_key=True, autoincrement=True)
    messages = db.relationship('ChatMessage', backref='chat', lazy='dynamic')
    rag_datas = db.relationship('RagData', backref='chat', lazy='dynamic')

    demanda_id = db.Column(db.Integer, db.ForeignKey('demanda.id_demanda'))