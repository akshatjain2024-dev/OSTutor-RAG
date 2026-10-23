import pickle
import numpy as np

import config


class Embedder:
    def __init__(self, backend: str = None):
        self.backend = backend or config.EMBED_BACKEND
        self.model = None
        self.vectorizer = None
        self.svd = None
        if self.backend in ("auto", "st"):
            try:
                from sentence_transformers import SentenceTransformer
                self.model = SentenceTransformer(config.EMBED_MODEL)
                self.backend = "st"
            except Exception as e:
                if self.backend == "st":
                    raise
                print(f"[embedder] sentence-transformers unavailable ({type(e).__name__}); "
                      f"using TF-IDF+SVD fallback")
                self.backend = "tfidf"

    @property
    def name(self):
        return config.EMBED_MODEL if self.backend == "st" else "tfidf-svd (offline)"

    def fit(self, texts):
        if self.backend != "tfidf":
            return self
        from sklearn.feature_extraction.text import TfidfVectorizer
        from sklearn.decomposition import TruncatedSVD
        self.vectorizer = TfidfVectorizer(ngram_range=(1, 2), sublinear_tf=True, max_features=30000,
                                          min_df=2 if len(texts) > 200 else 1, stop_words="english")
        X = self.vectorizer.fit_transform(texts)
        n_comp = max(2, min(256, X.shape[0] - 1, X.shape[1] - 1))
        self.svd = TruncatedSVD(n_components=n_comp, random_state=42).fit(X)
        self.svd.components_ = self.svd.components_.astype("float32")
        return self

    def _norm(self, v):
        v = np.asarray(v, dtype="float32")
        n = np.linalg.norm(v, axis=1, keepdims=True)
        n[n == 0] = 1
        return v / n

    def encode_docs(self, texts):
        if self.backend == "st":
            return self._norm(self.model.encode(texts, batch_size=32, show_progress_bar=True))
        return self._norm(self.svd.transform(self.vectorizer.transform(texts)))

    def encode_query(self, text):
        if self.backend == "st":
            prefix = ("Represent this sentence for searching relevant passages: "
                      if "bge" in config.EMBED_MODEL.lower() else
                      "query: " if "e5" in config.EMBED_MODEL.lower() else "")
            return self._norm(self.model.encode([prefix + text]))
        return self._norm(self.svd.transform(self.vectorizer.transform([text])))

    def save(self, path=config.EMBEDDER_PATH):
        with open(path, "wb") as f:
            pickle.dump({"backend": self.backend, "vectorizer": self.vectorizer,
                         "svd": self.svd}, f)

    @classmethod
    def load(cls, path=config.EMBEDDER_PATH):
        with open(path, "rb") as f:
            d = pickle.load(f)
        obj = cls.__new__(cls)
        obj.backend, obj.vectorizer, obj.svd, obj.model = d["backend"], d["vectorizer"], d["svd"], None
        if obj.backend == "st":
            from sentence_transformers import SentenceTransformer
            obj.model = SentenceTransformer(config.EMBED_MODEL)
        return obj
