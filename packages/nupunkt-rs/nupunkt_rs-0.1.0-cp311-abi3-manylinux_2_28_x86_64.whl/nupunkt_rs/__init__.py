"""
nupunkt-rs: High-performance Rust implementation of the Punkt sentence tokenizer

This module provides fast sentence boundary detection using the Punkt algorithm,
implemented in Rust for optimal performance.
"""

try:
    from ._nupunkt_rs import (
        AnalysisStatistics,
        DecisionFactor,
        InferenceConfig,
        Parameters,
        ScoringConfig,
        SentenceTokenizer,
        TextAnalysis,
        TokenAnalysis,
        Trainer,
        __version__,
        create_default_tokenizer,
        load_default_model,
        load_model,
        para_tokenize,
        para_tokenize_joined,
        sent_tokenize,
        train_model,
    )
except ImportError as e:
    # Fallback for development
    raise ImportError(
        "Could not import nupunkt_rs Rust extension. "
        "Make sure the package is built with: maturin develop"
    ) from e

__all__ = [
    "Parameters",
    "SentenceTokenizer",
    "ScoringConfig",
    "Trainer",
    "InferenceConfig",
    "TextAnalysis",
    "TokenAnalysis",
    "DecisionFactor",
    "AnalysisStatistics",
    "sent_tokenize",
    "para_tokenize",
    "para_tokenize_joined",
    "train_model",
    "load_model",
    "load_default_model",
    "create_default_tokenizer",
    "__version__",
]
