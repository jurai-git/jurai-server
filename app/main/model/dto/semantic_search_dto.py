
class SemanticSearchDTO:

    def __init__(self, processo, similarity: float):
        self.ementa = processo.ementa
        self.acordao = processo.acordao
        self.num_tjmg = processo.numero_tjmg
        self.sumula = processo.sumula
        self.similarity = similarity

    def serialize(self):
        return {
            'ementa': self.ementa,
            'acordao': self.acordao,
            'num_tjmg': self.num_tjmg,
            'sumula': self.sumula,
            'similarity': self.similarity
        }