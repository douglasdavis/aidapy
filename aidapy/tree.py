# -*- coding: utf-8 -*-

import ROOT
from .hist import shift_overflow

def tree2hist(tree,hist_name,binning,var,cut,overflow=False):
    """
    A function to create a histogram using TTree::Draw()

    Parameters
    ----------
    tree : The ROOT tree or chain
    hist_name : the name-in-memory of the histogram to be created
    binning : the binning of the histogram (nbins,xmin,xmax)
    var : string for the variable in the tree to histogram
    cut : the selection string

    Returns
    -------
    ROOT.TH1F
        The ROOT histogram created

    """
    ROOT.gROOT.SetBatch(True)
    ROOT.TH1.SetDefaultSumw2()
    if not isinstance(tree,ROOT.TTree):
        raise TypeError("Must be ROOT TTree or TChain")

    bin_str  = '('+str(binning[0])+','+str(binning[1])+','+str(binning[2])+')'
    tree.Draw(var+'>>'+hist_name+bin_str,cut)
    hist = ROOT.gDirectory.Get(hist_name)
    if overflow:
        shift_overflow(hist)
    return hist
