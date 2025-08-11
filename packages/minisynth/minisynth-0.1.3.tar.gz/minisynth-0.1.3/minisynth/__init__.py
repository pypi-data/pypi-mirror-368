"""MiniSynth - A modular synthesizer framework"""

from .MiniSynth import MiniSynth
from .MiniSynthFM import MiniSynthFM
from .MiniSynthSubtractive import MiniSynthSubtractive
from .WavetableGenerator import WavetableGenerator
from .ModGenerator import ModGenerator, Mod
from .DatasetManager import DatasetManager
from .Scale import Scale

__version__ = "0.1.0"
__all__ = [
    "MiniSynth",
    "MiniSynthFM", 
    "MiniSynthSubtractive",
    "WavetableGenerator",
    "ModGenerator",
    "Mod",
    "DatasetManager",
    "Scale"
]