"""Vector search over chunks. Two backends: TF-IDF (default) or sentence-transformers embeddings."""
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from .config import BACKEND, TOP_K


class Retriever:
    def __init__(self, chunks, backend: str = BACKEND):
        self.chunks, self.backend = chunks, backend
        texts = [c["text"] for c in chunks]
        if backend == "sbert":
            from sentence_transformers import SentenceTransformer
            self.model = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")
            self.matrix = self.model.encode(texts, normalize_embeddings=True)
        else:
            self.vec = TfidfVectorizer(ngram_range=(1, 2), sublinear_tf=True, stop_words="english")
            self.matrix = self.vec.fit_transform(texts)

    def search(self, query: str, k: int = TOP_K):
        if self.backend == "sbert":
            q = self.model.encode([query], normalize_embeddings=True)
            scores = (self.matrix @ q.T).ravel()
        else:
            scores = (self.matrix @ self.vec.transform([query]).T).toarray().ravel()
        idx = np.argsort(-scores)[:k]
        return [{**self.chunks[i], "score": round(float(scores[i]), 4)} for i in idx if scores[i] > 0]
