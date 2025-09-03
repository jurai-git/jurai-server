
class RetrievalEntry:
    def __init__(self, numero_tjmg, sumula, similarity):
        self.numero_tjmg = numero_tjmg
        self.sumula = sumula
        self.similarity = similarity
        self.acordao = None

    def add_acordao(self, acordao: str):
        self.acordao = acordao

    def __repr__(self):
        return f'{self.numero_tjmg} - [{self.sumula}: {self.similarity}]'
