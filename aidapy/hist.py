# -*- coding: utf-8 -*-
"""
Handling AIDA histograms
"""

import json
import math
from collections import namedtuple

import logging
from .logger import configure_logging
configure_logging()
logger  = logging.getLogger('aidapy')

from .meta import get_dsids
from .meta import _systematic_trees
from .meta import _systematic_weights
from .meta import _systematic_singles
from .meta import _systematic_ud_prefixes

import numpy as np

import ROOT

def hist2array(hist, include_overflow=False, copy=True, return_edges=False, return_err=False):
    """
    This algorithm is Copyright (c) 2012-2017, The root_numpy developers
    See disclaimer here: https://github.com/scikit-hep/root_numpy/blob/master/LICENSE

    This function is a small clone of root_numpy.hist2array for 1D histograms
    https://github.com/scikit-hep/root_numpy/blob/master/root_numpy/_hist.py

    Parameters
    ----------
    hist : ROOT TH1
        The ROOT histogram to convert
    include_overflow: bool, optional (default=False)
        If true, the over and underflow bins will be part of the array
    copy : bool, optional (default=True)
        If true copy the underlying array to own its memory
    return_edges : bool, optional (default=False)
        If true, return bin edges
    return_err : bool, optional (default=False)
        If true, return the sqrt(sum(weights squared))

    Returns
    -------
    hist : numpy array
        NumPy array with bin heights
    edges : list of numpy arrays
        A list of arrays. One for each axis' bin edges
    sumw2 : numpy array
        NumPy array of sqrt(sum(weights squared))
    """
    if isinstance(hist, ROOT.TH1F):
        dtype = 'f4'
    elif isinstance(hist, ROOT.TH1D):
        dtype = 'f8'
    else:
        raise TypeError('Must be ROOT.TH1F or ROOT.TH1D!')
    shape = (hist.GetNbinsX() +2,)
    array = np.ndarray(shape=shape, dtype=dtype, buffer=hist.GetArray())
    if return_err:
        error = np.sqrt(np.ndarray(shape=shape, dtype='f8',
                                   buffer=hist.GetSumw2().GetArray()))
    if return_edges:
        axis_getters, simple_hist, edges = ['GetXaxis'], True, []
        for idim, axis_getter in zip(range(1), axis_getters):
            ax = getattr(hist, axis_getter)(*(() if simple_hist else (idim,)))
            edges.append(np.empty(ax.GetNbins() + 1, dtype=np.double))
            ax.GetLowEdge(edges[-1])
            edges[-1][-1] = ax.GetBinUpEdge(ax.GetNbins())
    if not include_overflow:
        array = array[tuple([slice(1, -1) for idim in range(array.ndim)])]
        if return_err:
            error = error[tuple([slice(1, -1) for idim in range(error.ndim)])]

    array = np.transpose(array)
    if copy:
        array = np.copy(array)
    if return_err:
        error = np.transpose(error)
        if copy:
            error = np.copy(error)

    if return_edges and return_err:
        return array, edges, error
    if return_edges:
        return array, edges
    if return_err:
        return array, error
    return array

def shift_overflow(hist):
    """
    A function to shift the overflow bin in a ROOT
    histogram into the last bin. Only supports 1D histograms.

    Parameters
    ----------
    hist : The ROOT histogram

    """
    if not isinstance(hist, ROOT.TH1):
        raise TypeError("Argument must be 1D ROOT histogram!")
    nb = hist.GetNbinsX()
    val1, val2 = hist.GetBinContent(nb+1), hist.GetBinContent(nb)
    err1, err2 = hist.GetBinError(nb+1), hist.GetBinError(nb)
    hist.SetBinContent(nb, val1+val2)
    hist.SetBinError(nb, math.sqrt(err1*err1 + err2*err2))
    hist.SetBinContent(nb+1, 0.0)
    hist.SetBinError(nb+1, 0.0)

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
    if not isinstance(tree, ROOT.TTree):
        raise TypeError("Must be ROOT TTree or TChain")

    bin_str  = '('+str(binning[0])+','+str(binning[1])+','+str(binning[2])+')'
    tree.Draw(var+'>>'+hist_name+bin_str, cut)
    hist = ROOT.gDirectory.Get(hist_name)
    if overflow:
        shift_overflow(hist)
    return hist

_histProps  = namedtuple('_histProps',['var','binning','cut'])
def json2hists(jsonfile, outfilename='aida_histograms.root', tree_name='nominal'):
    """
    A function to generate histograms and store them in a ROOT file
    based on a json configuration

    Parameters
    ----------
    jsonfile : the input json file
    outfilename : the output ROOT file name
    tree_name : AIDA tree suffix (nominal, EG_RESOLUTION_ALL__1up, etc)
         if ALL, use run on all systematic trees defined in meta.py
    """
    if tree_name == 'ALL':
        json2hists(jsonfile,outfilename,'nominal')
        for tn in _systematic_trees:
            json2hists(jsonfile,outfilename,tn)
        return True
    topJson = json.load(open(jsonfile))
    hists   = dict()
    for hist in topJson['histograms']:
        if tree_name == 'nominal':
            logger.info('Histogram: '+hist['name']+
                        '\t| var: '+hist['var']+
                        '\t| bins: '+str(hist['bins'])+
                        '\t| cut: '+hist['cut'])
        hists[hist['name']] = _histProps._make([hist['var'],hist['bins'],hist['cut']])
    lumi       = topJson['lumi']
    proc_names = [ent.split('_')[0] for ent in topJson['dsids']] + ['Fakes']
    dsids      = { entry : get_dsids(entry) for entry in topJson['dsids'] }
    chains     = { entry : ROOT.TChain('AIDA_'+tree_name) for entry in dsids }
    chains['Fakes'] = ROOT.TChain('AIDAfk_'+tree_name)
    if tree_name == 'nominal':
        chains['Data'] = ROOT.TChain('AIDA_nominal')
        for f in topJson['datafiles']:
            chains['Data'].Add(f)
    for name, chain in chains.iteritems():
        if 'Fakes' in name: continue
        if 'Data' in name: continue
        for d in dsids[name]:
            adder = topJson['mcpath']+'/'+str(d)+'.root'
            chain.Add(adder)
            chains['Fakes'].Add(adder)

    out = ROOT.TFile(outfilename,'UPDATE')
    if 'AIDA_'+tree_name in out.GetListOfKeys():
        logger.warning('AIDA_'+tree_name+' already in output file')
        return False

    outd = out.mkdir('AIDA_'+tree_name)
    logger.info('Writing AIDA_'+tree_name)
    outd.cd()
    do_weight_sys = True
    for name, chain in chains.iteritems():
        for histn, props in hists.iteritems():
            weight_name = 'nomWeightwLum'
            if 'Data' in name: cut = props.cut
            else: cut = str(lumi)+'*'+weight_name+'*'+props.cut
            hname = name.split('_')[0]+'_'+histn
            h = tree2hist(chain,hname,props.binning,props.var,cut,overflow=True)
            h.Write()
            if tree_name == 'nominal' and 'Data' not in name and do_weight_sys:
                for systW in _systematic_weights:
                    for ud in systW:
                        logger.info('Writing weight syst histogram: '+hname)
                        cut = str(lumi)+'*'+ud+'*'+props.cut
                        hname = name.split('_')[0]+'_'+histn+'_'+ud.split('wLum_')[-1]
                        h = tree2hist(chain,hname,props.binning,props.var,cut,overflow=True)
                        h.Write()
    outd.Write()
    out.Close()
    return True

def totalsyshist(root_file, hist_name=None, proc_names=['ttbar','Wt','WW','Zjets','Diboson','Fakes']):
    """
    A function to calculate and return a histogram with a total
    systematic error band in numpy format.

    Parameters
    ----------
    root_file : the ROOT file with the histograms
    hist_name : the name of the histogram to generate the band for (must exist in ROOT file!)
    proc_names : the names of the processes contributing to the band (must exist in ROOT file!)

    Returns
    -------
    numpy.ndarray
       the nominal bin heights
    numpy.ndarray
       the systematic error in each bin
    numpy.ndarray
       the edges of the histogram bins

    """
    if hist_name is None:
        logger.error('Why no histogram name?')
        exit()

    nominals   = { pname : root_file.Get('AIDA_nominal/'+pname+'_'+hist_name) for pname in proc_names }
    nominals   = { pname : hist2array(h,return_edges=True) for pname, h in nominals.iteritems() }
    edges      = nominals['ttbar'][1][0]
    nbins      = len(nominals['ttbar'][0])
    total_band = np.zeros(nbins,dtype=np.float32)
    nom_h      = np.zeros(nbins,dtype=np.float32)
    for pname, nom in nominals.iteritems():
        nom_h = nom_h + nom[0]
    for pname in proc_names:
        proc_nom = nominals[pname][0]
        # the two sided systematics in trees
        for ud in _systematic_ud_prefixes:
            if 'MET_Soft' in ud: updown = ['Up/','Down/'] # why does MET use different name... lame
            else:                updown = ['__1up/','__1down/']
            for ud2 in updown:
                arr = hist2array(root_file.Get('AIDA_'+ud+ud2+pname+'_'+hist_name))
                total_band = total_band + (proc_nom-arr)*(proc_nom-arr)
        # the one sided systematics in trees, symmetrize it
        for osed in _systematic_singles:
            arr = hist2array(root_file.Get('AIDA_'+osed+'/'+pname+'_'+hist_name))
            total_band = total_band + 2*(proc_nom-arr)*(proc_nom-arr)
        # the hists from weights
        for wud in _systematic_weights:
            u_ws, d_ws = wud[0].split('wLum_')[-1], wud[1].split('wLum_')[-1]
            for ws in [u_ws,d_ws]:
                arr = hist2array(root_file.Get('AIDA_nominal/'+pname+'_'+hist_name+'_'+ws))
                total_band = total_band + (proc_nom-arr)*(proc_nom-arr)
    # root that summed quadrature.
    total_band = np.sqrt(total_band)
    return nom_h, total_band, edges
