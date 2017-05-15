from __future__ import print_function
import ROOT
ROOT.gROOT.SetBatch(True)
import numpy as np
from aidapy.hist import array2hist
from aidapy.hist import hist2array
from aidapy.hist import total_systematic_histogram
import root_utils

def canvas_with_ratio(name, xdim=450, ydim=475,
                      pad0=(0.0,0.28,0.95,0.95),
                      pad1=(0.0,0.00,0.95,0.27)):
    """
    Create a ROOT TCanvas with two pads, one for a ratio

    Parameters
    ----------
    name: str
      Name of the canvas
    xdim: int
      Width of the canvas
    ydim: int
      height of the canvas
    pad0: tuple (floats)
      the ROOT TPad dimension fractions (main pad)
    pad1: tuple (floats)
      the ROOT TPad dimension fractions (ratio pad)

    Returns
    -------
    ROOT.TCanvas
      The ROOT Canvas
    ROOT.TPad
      The main ROOT TPad
    ROOT.TPad
      The ratio ROOT TPad
    """
    canvas = ROOT.TCanvas(name, name, xdim, ydim)
    pad0   = ROOT.TPad(name+'pad0', name+'pad0', pad0[0], pad0[1], pad0[2], pad0[3])
    pad1   = ROOT.TPad(name+'pad1', name+'pad1', pad1[0], pad1[1], pad1[2], pad1[3])
    pad0.SetBottomMargin(0.0275)
    pad0.SetTopMargin(0.0685)
    pad0.SetRightMargin(.0255)
    pad1.SetTopMargin(0.015)
    pad1.SetRightMargin(.0255)
    pad1.SetBottomMargin(0.40)
    pad1.SetFrameFillColor(0)
    pad1.SetFrameBorderMode(0)
    return canvas, pad0, pad1

def hist_formatting(chist,isdata=False,logging=False):
    chist.SetMarkerStyle(8)
    chist.SetMarkerSize(.75)
    chist.GetXaxis().SetLabelOffset(99)
    chist.GetXaxis().SetTitleOffset(99)
    if isdata:
        chist.SetLineWidth(1)
        chist.SetMaximum(chist.GetMaximum()*1.4)
        if logging:
            chist.SetMaximum(chist.GetMaximum()*25)
            chist.SetMinimum(10.0)
        chist.GetYaxis().SetTickLength(0.02)

def hplot_root(root_file, hist_name='met_1pj', xtitle='', ytitle='', logy=False,
               proc_names=['ttbar','Wt','Ztautau','WW','Diboson','Fakes','RareSM'],
               colors=[ROOT.kWhite,ROOT.kBlue,ROOT.kOrange,ROOT.kGreen,ROOT.kBlack,ROOT.kGray,ROOT.kRed]):
    """
    Plot histograms using ROOT
    """
    nominals = { pname : root_file.Get(pname+'_FULL_main_nominal_'+hist_name) for pname in proc_names }
    data     = root_file.Get('Data_'+hist_name)
    data.SetMinimum(0.0)
    data_a   = hist2array(data)
    nom_h, total_band, edges, staterr = total_systematic_histogram(root_file, hist_name, proc_names,
                                                                   return_stat_error=True)
    ratio_a         = data_a/nom_h
    ratio_a_staterr = np.sqrt(1/(nom_h*nom_h)*data_a + np.power(data_a/(nom_h*nom_h)*staterr,2))
    ratio_root_h    = array2hist(ratio_a, errors=ratio_a_staterr)
    sysh = array2hist(nom_h, 'totalSys_'+hist_name, (nom_h.size,edges[0],edges[-1]), errors=total_band)
    ratiosysh = array2hist(np.array(np.ones(nom_h.size)), 'totalSysRatio_'+hist_name,
                           (nom_h.size,edges[0],edges[-1]), errors=total_band/nom_h)
    root_stack = ROOT.THStack('stack_'+hist_name, 'stack_'+hist_name)
    for pname, col in zip(proc_names[::-1], colors[::-1]):
        nominals[pname].SetFillColor(col)
        nominals[pname].SetLineColor(ROOT.kBlack)
        hist_formatting(nominals[pname])
        root_stack.Add(nominals[pname])
    hist_formatting(data, isdata=True, logging=logy)

    c, p0, p1 = canvas_with_ratio(hist_name)
    p0.cd()
    data.Draw('e')
    root_stack.Draw('hist,same')
    sysh.Draw('e2,same')
    sysh.SetFillStyle(3003)
    sysh.SetFillColor(ROOT.kBlack)
    sysh.SetMarkerSize(0)
    data.Draw('same,e')
    p1.cd()
    ratiosysh.SetFillStyle(3003)
    ratiosysh.SetFillColor(ROOT.kBlack)
    ratiosysh.SetMarkerSize(0)
    ratio_root_h.Draw('e,same')
    ratio_root_h.SetMinimum(0.5)
    ratio_root_h.SetMaximum(1.5)
    ratiosysh.Draw('e2,same')
    c.cd()
    p0.Draw()
    p1.Draw()
    p0.RedrawAxis()
    p1.RedrawAxis()
    c.SaveAs(hist_name+'.pdf')
    ROOT.SetOwnership(p0,False)
    ROOT.SetOwnership(p1,False)
    ROOT.SetOwnership(c,False)
