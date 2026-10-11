"""Affect and motivation layer.

Low-dimensional, explicitly-defined state variables (reward prediction error,
valence, arousal, threat, frustration) with documented update rules. These are
*candidate modelling constructs* inspired by computational affective
neuroscience, NOT measured biological quantities and NOT claims about
subjective feeling.
"""

from neuralmind.affect.reward import RewardPredictor
from neuralmind.affect.affect_state import AffectState, AffectParams

__all__ = ["RewardPredictor", "AffectState", "AffectParams"]
