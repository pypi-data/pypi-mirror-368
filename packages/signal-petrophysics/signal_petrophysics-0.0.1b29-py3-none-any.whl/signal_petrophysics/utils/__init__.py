# src/signal_petrophysics/utils/__init__.py

"""Utilities module for signal petrophysics package."""

# Import the mnemonic lists, functions, AND mnemonic_dict from mnemonics.py
from .mnemonics import (
    # Mnemonic lists
    gamma_names,
    sp_names,
    caliper_names,
    deepres_names,
    rxo_names,
    density_names,
    density_correction_names,
    neutron_names,
    dtc_names,
    dts_names,
    pe_names,
    
    # The module-level mnemonic_dict - THIS WAS MISSING!
    mnemonic_dict,
    
    # Functions
    find_column,
    create_mnemonic_dict
)

# Define what gets exported when using "from utils import *"
__all__ = [
    # Mnemonic lists
    'gamma_names',
    'sp_names', 
    'caliper_names',
    'deepres_names',
    'rxo_names',
    'density_names',
    'density_correction_names',
    'neutron_names',
    'dtc_names',
    'dts_names',
    'pe_names',
    
    # The module-level mnemonic_dict
    'mnemonic_dict',
    
    # Functions
    'find_column',
    'create_mnemonic_dict'
]

# Optional: Create a convenience dictionary for easy access
MNEMONIC_LISTS = {
    'gamma': gamma_names,
    'sp': sp_names,
    'caliper': caliper_names,
    'deepres': deepres_names,
    'rxo': rxo_names,
    'density': density_names,
    'density_correction': density_correction_names,
    'neutron': neutron_names,
    'dtc': dtc_names,
    'dts': dts_names,
    'pe': pe_names
}
