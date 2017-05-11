"""
Module for generating and manipulation histograms for AIDA
"""

from .utils import hist2array
from .utils import array2hist
from .utils import shift_overflow
from .utils import tree2hist
from .gen import generate_mc_hists
from .gen import generate_data_hists
from .gen import generate_hists
from .gen import total_systematic_histogram

__ALL__ = [
    'hist2array',
    'array2hist',
    'shift_overflow',
    'tree2hist',
    'generate_mc_hists',
    'generate_data_hists',
    'generate_hists',
    'total_systematic_histogram',
]
