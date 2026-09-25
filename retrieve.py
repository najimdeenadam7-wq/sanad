"""Dependency-free BM25 retrieval. Extension point: swap for embeddings + pgvector in pilot."""
import math, re
from collections import Counter

def _tok(t): return re.findall(r"[a-z0-9%$.]+", t.lower())

class BM25:
    def __init__(self, chunks):
        self.chunks = chunks
        self.docs = [_tok(c.text) for c in chunks]
        self.N = len(chunks)
        self.avgdl = sum(map(len, self.docs)) / max(self.N, 1)
        df = Counter()
        for d in self.docs: df.update(set(d))
        self.idf = {t: math.log(1 + (self.N - n + .5) / (n + .5)) for t, n in df.items()}
    def search(self, query, k=4):
        q, scores = _tok(query), []
        for i, d in enumerate(self.docs):
            tf, dl, s = Counter(d), len(d), 0.0
            for t in q:
                if t in self.idf:
                    f = tf.get(t, 0)
                    s += self.idf[t] * f * 2.5 / (f + 1.5 * (.25 + .75 * dl / self.avgdl))
            scores.append((s, i))
        scores.sort(reverse=True)
        return [self.chunks[i] for s, i in scores[:k] if s > 0]