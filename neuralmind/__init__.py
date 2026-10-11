"""NeuralMind: a local-first, reproducible computational brain-simulation platform.

NeuralMind is a research/experimentation toolkit, NOT a biologically complete
brain and NOT a conscious or sentient system. It implements scientifically
grounded but deliberately simplified mechanisms (leaky integrate-and-fire
neurons, spike-timing-dependent plasticity, reward-modulated learning, and a
low-dimensional affect/motivation layer). Every module documents where it uses
an engineering approximation rather than a validated biological finding.

The core simulation engine depends only on NumPy and runs on an ordinary
developer machine with no external API key.
"""

__version__ = "0.2.0"

from neuralmind.core.neurons import LIFPopulation, LIFParams
from neuralmind.core.network import SpikingNetwork
from neuralmind.core.plasticity import STDPConfig, STDPSynapse

__all__ = [
    "__version__",
    "LIFPopulation",
    "LIFParams",
    "SpikingNetwork",
    "STDPConfig",
    "STDPSynapse",
]
