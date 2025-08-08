"""
Syllabify: Automatically convert plain text into phonemes and syllabify.

This package provides tools for phonetic transcription and syllabification
using the CMU Pronouncing Dictionary.
"""

from importlib.metadata import version, PackageNotFoundError

try:
    __version__ = version("syllabify")
except PackageNotFoundError:
    __version__ = "unknown"

# These imports might fail if the files aren't ready yet, so we'll handle gracefully
try:
    from syllabify.core import syllabify, transcribe
    from syllabify.phonemes import (
        Phoneme,
        Vowel,
        Consonant,
    )
    from syllabify.syllables import (
        Cluster,
        Empty,
        Rime,
        Syllable,
        Word,
        Sentence,
    )
    from syllabify.constants import VOWEL_TYPES

    __all__ = [
        "syllabify",
        "transcribe",
        "Cluster",
        "Phoneme",
        "Consonant",
        "Vowel",
        "Empty",
        "Rime",
        "Syllable",
        "Word",
        "Sentence",
        "VOWEL_TYPES",
    ]
except ImportError:
    # If imports fail, just provide basic info
    __all__ = []
