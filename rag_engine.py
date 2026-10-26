"""
rag_engine.py
--------------
Implements the Retrieval-Augmented Generation (RAG) backbone of the
Smart Travel Planning Assistant.

Pipeline:
1. Load travel guide PDFs from data/pdfs/
2. Split each document into overlapping text chunks
3. Build a TF-IDF vector space over all chunks (acts as the embedding /
   vector-database layer - no external API key or internet model
   download required, keeping the whole project runnable offline)
4. Given a natural-language query, retrieve the most semantically
   similar chunks (cosine similarity) together with their source
   document, so the assistant can always cite where an answer came from
   (this is what makes the retrieval "Agentic RAG": the agent decides
   *when* to call this tool and *how many* documents to pull in).
"""

import os
import glob
from dataclasses import dataclass
from typing import List

from pypdf import PdfReader
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


@dataclass
class Chunk:
    text: str
    source: str
    chunk_id: int


class VectorStore:
    """A lightweight, dependency-free (no internet) vector database."""

    def __init__(self, chunk_size: int = 120, chunk_overlap: int = 30):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.chunks: List[Chunk] = []
        self.vectorizer = TfidfVectorizer(stop_words="english")
        self.matrix = None

    # ---------- Loading & Indexing ----------
    def load_pdfs(self, pdf_dir: str):
        pdf_paths = sorted(glob.glob(os.path.join(pdf_dir, "*.pdf")))
        if not pdf_paths:
            raise FileNotFoundError(f"No PDF files found in {pdf_dir}")
        for path in pdf_paths:
            text = self._extract_text(path)
            self._add_document(text, source=os.path.basename(path))
        self._build_index()
        return self

    @staticmethod
    def _extract_text(path: str) -> str:
        reader = PdfReader(path)
        return "\n".join(page.extract_text() or "" for page in reader.pages)

    def _add_document(self, text: str, source: str):
        words = text.split()
        step = self.chunk_size - self.chunk_overlap
        cid = 0
        for start in range(0, len(words), step):
            piece = " ".join(words[start:start + self.chunk_size])
            if piece.strip():
                self.chunks.append(Chunk(text=piece, source=source, chunk_id=cid))
                cid += 1
            if start + self.chunk_size >= len(words):
                break

    def _build_index(self):
        corpus = [c.text for c in self.chunks]
        self.matrix = self.vectorizer.fit_transform(corpus)

    # ---------- Retrieval ----------
    def search(self, query: str, top_k: int = 3):
        """Return the top_k most relevant chunks with similarity scores."""
        if self.matrix is None:
            raise RuntimeError("Vector store not built. Call load_pdfs() first.")
        q_vec = self.vectorizer.transform([query])
        sims = cosine_similarity(q_vec, self.matrix).flatten()
        ranked = sims.argsort()[::-1][:top_k]
        results = []
        for idx in ranked:
            if sims[idx] <= 0:
                continue
            results.append({
                "text": self.chunks[idx].text,
                "source": self.chunks[idx].source,
                "score": round(float(sims[idx]), 4),
            })
        return results
