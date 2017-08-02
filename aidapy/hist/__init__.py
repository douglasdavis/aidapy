"""
Module for generating and manipulating histograms for AIDA
"""

from .utils import bin_centers
from .utils import hist2array
from .utils import array2hist
from .utils import shift_overflow
from .utils import tree2hist
from .utils import np_selection
from .utils import np_hist

from .gen import generate_mc_hists
from .gen import generate_data_hists
from .gen import generate_hists
from .gen import total_systematic_histogram

__ALL__ = [
    'bin_centers',
    'hist2array',
    'array2hist',
    'shift_overflow',
    'tree2hist',
    'generate_mc_hists',
    'generate_data_hists',
    'generate_hists',
    'total_systematic_histogram',
    'np_selection',
    'np_hist'
]
