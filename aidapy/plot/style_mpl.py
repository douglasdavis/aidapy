# Copyright 2012 the rootpy developers
# distributed under the terms of the GNU General Public License
"""
ATLAS-like style for matplotlib
"""

def style_mpl():

    STYLE = {}

    STYLE['lines.linewidth'] = 1

    # font
    STYLE['font.sans-serif'] = 'helvetica, Helvetica, Nimbus Sans L, Mukti Narrow, FreeSans'
    STYLE['font.family'] = 'sans-serif'
    #STYLE['mathtext.fontset'] = 'stixsans'
    STYLE['mathtext.fontset'] = 'dejavusans'
    #STYLE['mathtext.fontset'] = 'stix'
    STYLE['mathtext.default'] = 'rm'
    # helvetica usually not present on linux
    #STYLE['text.usetex'] = True

    # figure layout
    STYLE['figure.figsize'] = 8.75, 5.92
    #   atlasStyle->SetPaperSize(20,26); # in cm
    # STYLE['figure.figsize'] =  10.2362205, 7.874015 # in inc, not working
    STYLE['figure.facecolor'] = 'white'
    STYLE['figure.subplot.bottom'] = 0.12
    STYLE['figure.subplot.top'] = 0.95
    STYLE['figure.subplot.left'] = 0.12
    STYLE['figure.subplot.right'] = 0.95

    # axes
    STYLE['axes.labelsize'] = 16
    STYLE['xtick.labelsize'] = 14
    STYLE['xtick.major.size'] = 8
    STYLE['xtick.minor.size'] = 4
    STYLE['ytick.labelsize'] = 14
    STYLE['ytick.major.size'] = 11
    STYLE['ytick.minor.size'] = 5
    STYLE['lines.markersize'] = 8
    # STYLE['lines.markeredgewidth'] = 0. # not working, it changes other stuff

    # legend
    STYLE['legend.numpoints'] = 1
    STYLE['legend.fontsize'] = 14
    STYLE['legend.labelspacing'] = 0.3
    STYLE['legend.frameon'] = False

    # what cannot be set with rcParams:
    # * markeredgewidth
    # * axis-label alignment
    # * axis-label offset
    # * axis-ticks

    return STYLE
