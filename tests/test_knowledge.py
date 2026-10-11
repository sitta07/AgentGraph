"""Tests for the source-cited knowledge index (Subsystem B)."""

from neuralmind.knowledge.index import KnowledgeIndex


def _index():
    idx = KnowledgeIndex()
    idx.ingest_text(
        "stdp",
        "Spike-timing-dependent plasticity strengthens a synapse when the\n"
        "presynaptic spike precedes the postsynaptic spike.\n\n"
        "Reward prediction error modulates learning as a third factor.",
        source="SCIENTIFIC_EVIDENCE.md",
    )
    idx.ingest_text(
        "affect",
        "The circumplex model describes affect with valence and arousal.",
        source="affect_notes.md",
    )
    return idx


def test_ingest_counts_passages():
    idx = KnowledgeIndex()
    n = idx.ingest_text("d", "para one\n\npara two", source="s")
    assert n == 2
    assert len(idx) == 2


def test_search_returns_relevant_passage_with_source():
    idx = _index()
    results = idx.search("presynaptic postsynaptic spike timing", top_k=3)
    assert results
    top = results[0]
    assert top.doc_id == "stdp"
    assert top.source == "SCIENTIFIC_EVIDENCE.md"
    assert "plasticity" in top.text.lower()
    # Traceable citation string.
    assert "SCIENTIFIC_EVIDENCE.md" in top.citation
    assert "passage" in top.citation


def test_search_ranks_by_relevance():
    idx = _index()
    results = idx.search("valence arousal affect", top_k=5)
    assert results[0].doc_id == "affect"


def test_empty_query_returns_nothing():
    assert _index().search("") == []


def test_unmatched_query_returns_nothing():
    assert _index().search("xyzzy quux nonexistentterm") == []


def test_scores_are_descending():
    idx = _index()
    results = idx.search("spike reward learning", top_k=5)
    scores = [r.score for r in results]
    assert scores == sorted(scores, reverse=True)
