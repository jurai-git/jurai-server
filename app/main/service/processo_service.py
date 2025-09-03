from typing import List

from flask_sqlalchemy import SQLAlchemy
from app.main.model.processo import Processo

class ProcessoService:

    def __init__(self, db: SQLAlchemy):
        self.db = db

    def get_all_by_num_tjmg(self, nums_tjmg: List[str]):
        return self.db.session.query(Processo).filter(Processo.numero_tjmg.in_(nums_tjmg)).all()
