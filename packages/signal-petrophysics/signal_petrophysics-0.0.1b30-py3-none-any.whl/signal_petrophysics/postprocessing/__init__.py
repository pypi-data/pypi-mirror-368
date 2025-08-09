# Import required functions from other modules that are used in postprocessing
from ..pattern_find import signal_sampling_by_depth, auto_similarity
from ..signal_adapt import adjust_signal_length

"""Postprocessing module for signal petrophysics package."""

# Import functions from the postprocessing module
from .postprocessing import (
    process_depth_ranges,
    merge_and_label_dataframes,
    export_labeled_logs_to_csv,
    concatenate_all_depth_ranges,
    extend_labels
)

# Define what gets exported when using "from postprocessing import *"
__all__ = [
    'process_depth_ranges',
    'merge_and_label_dataframes', 
    'export_labeled_logs_to_csv',
    'concatenate_all_depth_ranges',
    'extend_labels'
]
