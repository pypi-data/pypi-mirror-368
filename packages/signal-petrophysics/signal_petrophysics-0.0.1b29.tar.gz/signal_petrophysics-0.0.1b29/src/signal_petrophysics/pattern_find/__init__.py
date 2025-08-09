# src/signal_petrophysics/pattern_find/__init__.py

from .pattern_find import (
    signal_sampling_by_depth,
    auto_similarity,
    generate_stencils,
    calc_cca,
    offset_similarity,
    process_corr,
    calc_corr
)

__all__ = [
    'signal_sampling_by_depth',
    'auto_similarity', 
    'generate_stencils',
    'calc_cca',
    'offset_similarity',
    'process_corr',
    'calc_corr'
]
