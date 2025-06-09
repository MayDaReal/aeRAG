# tests/test_embeddings.py
from embeddings.embeddings import SentenceTransformerEmbeddingModel

def test_embedding_dim():
    model = SentenceTransformerEmbeddingModel()
    vec = model.encode("Hello Archethic")
    assert isinstance(vec, list)
    assert len(vec) == 384      # all-MiniLM-L6-v2 default
    assert all(isinstance(x, float) for x in vec)
