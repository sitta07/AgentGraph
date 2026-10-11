"""A tiny TF-IDF document index with traceable source references.

Design
------
* Documents are ingested as text with an explicit ``source`` and ``doc_id``.
* Each document is split into passages (by blank lines); each passage is a
  retrievable unit so citations point at a specific span, not a whole file.
* Retrieval scores passages against the query with TF-IDF cosine similarity.
* Every :class:`SearchResult` reports ``doc_id`` and ``source`` so the origin of
  any retrieved text can be checked.

Standard library only (``re``, ``math``, ``collections``). This is deliberately
simple keyword retrieval; it makes no claim to semantic understanding and is
explicitly distinct from the simulator's learned weights (see the package
docstring and ADR-0007).
"""

from __future__ import annotations

import math
import re
from collections import Counter
from dataclasses import dataclass, field
from pathlib import Path

_TOKEN = re.compile(r"[a-z0-9]+")


def _tokenize(text: str) -> list[str]:
    return _TOKEN.findall(text.lower())


@dataclass
class _Passage:
    doc_id: str
    source: str
    passage_index: int
    text: str
    metadata: dict
    tf: Counter = field(default_factory=Counter)


@dataclass
class SearchResult:
    doc_id: str
    source: str
    passage_index: int
    text: str
    score: float
    metadata: dict

    @property
    def citation(self) -> str:
        """Human-readable, traceable source reference."""
        return f"{self.source} (doc={self.doc_id}, passage #{self.passage_index})"


class KnowledgeIndex:
    """In-memory TF-IDF passage index with provenance."""

    def __init__(self) -> None:
        self._passages: list[_Passage] = []
        self._df: Counter = Counter()      # document frequency per term
        self._dirty = True
        self._idf: dict[str, float] = {}

    # ---- ingestion -------------------------------------------------------
    def ingest_text(self, doc_id: str, text: str, source: str,
                    metadata: dict | None = None) -> int:
        """Add a document; returns the number of passages indexed."""
        metadata = metadata or {}
        passages = [p.strip() for p in re.split(r"\n\s*\n", text) if p.strip()]
        for idx, passage in enumerate(passages):
            tf = Counter(_tokenize(passage))
            if not tf:
                continue
            self._passages.append(
                _Passage(doc_id, source, idx, passage, dict(metadata), tf)
            )
            for term in tf:
                self._df[term] += 1
        self._dirty = True
        return len(passages)

    def ingest_file(self, path: str | Path, doc_id: str | None = None) -> int:
        """Ingest a local text/markdown file, using its path as the source."""
        p = Path(path)
        text = p.read_text(encoding="utf-8", errors="replace")
        return self.ingest_text(doc_id or p.name, text, source=str(p))

    # ---- retrieval -------------------------------------------------------
    def _recompute_idf(self) -> None:
        n = max(1, len(self._passages))
        self._idf = {
            term: math.log((1 + n) / (1 + df)) + 1.0
            for term, df in self._df.items()
        }
        self._dirty = False

    def _vector(self, tf: Counter) -> dict[str, float]:
        return {t: c * self._idf.get(t, 0.0) for t, c in tf.items()}

    def search(self, query: str, top_k: int = 5) -> list[SearchResult]:
        """Return the top-k passages most relevant to the query, with sources."""
        if self._dirty:
            self._recompute_idf()
        q_vec = self._vector(Counter(_tokenize(query)))
        if not q_vec:
            return []
        q_norm = math.sqrt(sum(v * v for v in q_vec.values()))
        if q_norm == 0:
            return []

        scored: list[SearchResult] = []
        for p in self._passages:
            d_vec = self._vector(p.tf)
            dot = sum(q_vec.get(t, 0.0) * v for t, v in d_vec.items())
            if dot <= 0:
                continue
            d_norm = math.sqrt(sum(v * v for v in d_vec.values()))
            score = dot / (q_norm * d_norm) if d_norm else 0.0
            if score > 0:
                scored.append(SearchResult(
                    doc_id=p.doc_id, source=p.source, passage_index=p.passage_index,
                    text=p.text, score=round(score, 6), metadata=p.metadata,
                ))
        scored.sort(key=lambda r: r.score, reverse=True)
        return scored[:top_k]

    def __len__(self) -> int:
        return len(self._passages)
