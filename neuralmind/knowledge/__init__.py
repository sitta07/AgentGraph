"""Subsystem B: a local, source-cited knowledge/document index.

This is a *document retrieval* layer for scientific notes, references, and
experiment logs. It uses keyword / TF-IDF scoring from the Python standard
library only (no embeddings, no API key). Every result carries an explicit
**source reference** (document id + origin) so retrieved text is traceable.

IMPORTANT separation of concerns: this index is NOT biological memory and NOT
the learned synaptic weights of the simulator. Vector/keyword similarity over
documents is a different kind of "memory" from the network's plastic weights,
its transient simulation state, and the experiment history in
``persistence``. See ADR-0007.
"""

from neuralmind.knowledge.index import KnowledgeIndex, SearchResult

__all__ = ["KnowledgeIndex", "SearchResult"]
