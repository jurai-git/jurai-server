from typing import List

from pinecone.grpc import PineconeGRPC as Pinecone
from sentence_transformers import SentenceTransformer
import torch
from dotenv import load_dotenv

from models.rag.purify import preprocess_semantic_search
from models.rag.retrieval_entry import RetrievalEntry


class Retriever:
    def __init__(self, pinecone_api_key, pinecone_index_url):
        load_dotenv()

        # initialize embedding model
        self.model = SentenceTransformer('sentence-transformers/paraphrase-multilingual-mpnet-base-v2')
        if torch.cuda.is_available():
            self.model.to('cuda')
            print('Initialized SentenceTransformer on CUDA')
        else:
            print('Initialized SentenceTransformer on CPU')

        # initialize pinecone DB
        self.pc = Pinecone(api_key=pinecone_api_key)
        self.index = self.pc.Index(host=pinecone_index_url)

    def semantic_search(self, search: str, count: int = 3) -> List[RetrievalEntry]:
        search = preprocess_semantic_search(search)
        embeddings = self._embed(search)

        results = self.index.query(
            vector=embeddings,
            top_k=count,
            include_metadata=True,
            include_values=False
        )['matches']

        entries: List[RetrievalEntry] = []
        for result in results:
            entries.append(RetrievalEntry(
                numero_tjmg=result['id'],
                sumula=result['metadata']['sumula'],
                similarity=result['score']
            ))

        return entries

    def _embed(self, string: str):
        return self.model.encode(string).tolist()

    def _embed_batch(self, batch: List[str]):
        return self.model.encode(batch).tolist()