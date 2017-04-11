# -*- coding: utf-8 -*-

import math
import ROOT

def shift_overflow(hist):
    """
    A function to shift the overflow bin in a ROOT
    histogram into the last bin. Only supports 1D histograms.

    Parameters
    ----------
    hist : The ROOT histogram

    """
    if not isinstance(hist,ROOT.TH1):
        raise TypeError("Argument must be 1D ROOT histogram!")
    nb = hist.GetNbinsX()
    val1, val2 = hist.GetBinContent(nb+1), hist.GetBinContent(nb)
    err1, err2 = hist.GetBinError(nb+1), hist.GetBinError(nb)
    hist.SetBinContent(nb,val1+val2)
    hist.SetBinError(nb,math.sqrt(err1*err1 + err2*err2))
    hist.SetBinContent(nb+1,0.0)
    hist.SetBinError(nb+1,0.0)
