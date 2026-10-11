"""Reproducible multi-seed research experiments built on the NeuralMind world.

Each experiment fixes its hypotheses, conditions, seeds and metrics *before*
running, reports means with bootstrap 95% confidence intervals, and writes the
raw per-run numbers to disk so results can be re-analysed or challenged.
"""
