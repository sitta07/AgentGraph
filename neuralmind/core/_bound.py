"""Rebinding guard for arrays that a fused network stacks."""

from __future__ import annotations

STACKED = frozenset({"weights", "_i_syn", "x_pre", "x_post", "eligibility", "v", "refractory_left"})


class Bound:
    """Marks the owning fused network stale when one of its stacked arrays is
    replaced by a different object. In-place updates (``a += b``) rebind the
    same object and do not count."""

    def __setattr__(self, name: str, value) -> None:
        if name in STACKED:
            owner = self.__dict__.get("_fused_owner")
            if owner is not None and self.__dict__.get(name) is not value:
                owner.dirty = True
        object.__setattr__(self, name, value)
