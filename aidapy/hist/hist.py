# -*- coding: utf-8 -*-
"""
Handling AIDA histograms
"""

from __future__ import print_function

import json
import math
from collections import namedtuple

import logging
from .. import configure_logging
configure_logging()
logger  = logging.getLogger('aidapy')

from aidapy.meta import get_dsids
from aidapy.meta import get_proc_gen
from aidapy.meta import proc_gen_from_file
from aidapy.meta import sort_files_from_txt
from aidapy.meta import _systematic_trees
from aidapy.meta import _systematic_weights
from aidapy.meta import _systematic_singles
from aidapy.meta import _systematic_ud_prefixes

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
    hist : numpy.ndarray
        NumPy array with bin heights
    edges : list of numpy.ndarray
        A list of arrays. One for each axis' bin edges
    error : numpy.ndarray
        NumPy array of sqrt(sum(weights squared))
    """
    if isinstance(hist, ROOT.TH1F):
        dtype = 'f4'
    elif isinstance(hist, ROOT.TH1D):
        dtype = 'f8'
    else:
        print(hist,hist.GetName())
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
        raise TypeError('Argument must be 1D ROOT histogram!')
    nb = hist.GetNbinsX()
    val1, val2 = hist.GetBinContent(nb+1), hist.GetBinContent(nb)
    err1, err2 = hist.GetBinError(nb+1), hist.GetBinError(nb)
    hist.SetBinContent(nb, val1+val2)
    hist.SetBinError(nb, math.sqrt(err1*err1 + err2*err2))
    hist.SetBinContent(nb+1, 0.0)
    hist.SetBinError(nb+1, 0.0)

def tree2hist(tree, hist_name, binning, var, cut, overflow=False):
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
    if not isinstance(tree, ROOT.TTree):
        raise TypeError('Must be ROOT TTree or TChain')
    ROOT.TH1.SetDefaultSumw2()
    bin_str  = '('+str(binning[0])+','+str(binning[1])+','+str(binning[2])+')'

    # if the tree/chain is empty, just make an empty histogram.
    if tree.GetEntries() == 0:
        print('making an empty',hist_name)
        hist = ROOT.TH1F(hist_name,hist_name,binning[0],binning[1],binning[2])
        return hist

    tree.Draw(var+'>>'+hist_name+bin_str, cut, 'goff')
    hist = ROOT.gDirectory.Get(str(hist_name))
    if overflow:
        shift_overflow(hist)
    return hist

def json2hists(jsonfile, outfilename='aida_histograms.root', tree_name='nominal'):

    """
    A function to generate histograms and store them in a ROOT file
    based on a json configuration

    Parameters
    ----------
    jsonfile : the input json file
    outfilename : the output ROOT file name
    tree_name : AIDA tree suffix (nominal, EG_RESOLUTION_ALL__1up, etc)
         if ALL, use on all systematic trees defined in meta.py
    """

    _histProps  = namedtuple('_histProps',['var','binning','cut'])
    if tree_name == 'ALL':
        json2hists(jsonfile,outfilename,'nominal')
        for tn in _systematic_trees:
            json2hists(jsonfile,outfilename,tn)
        return True
    topJson = json.load(open(jsonfile))
    lumi    = topJson['lumi']
    logger.info('Scaling to '+str(lumi)+' /fb')
    hists   = {}
    for hist in topJson['histograms']:
        if tree_name == 'nominal':
            logger.info('Histogram: '+hist['name']+
                        '\t| var: '+hist['var']+
                        '\t| bins: '+str(hist['bins'])+
                        '\t| cut: '+hist['cut'])
        hists[hist['name']] = _histProps._make([hist['var'],hist['bins'],hist['cut']])

    sorted_files = sort_files_from_txt(topJson['files'],topJson['procs'])
    chains = { k.split('_')[0] : ROOT.TChain('AIDA_'+tree_name) for k in sorted_files }
    chains['Fakes'] = ROOT.TChain('AIDAfk_'+tree_name)
    for k, v in sorted_files.items():
        if k == 'Data' and tree_name != 'nominal':
            continue
        for vv in v:
            chains[k.split('_')[0]].Add(vv)
            if 'Data' not in k:
                chains['Fakes'].Add(vv)

    out = ROOT.TFile(outfilename,'UPDATE')
    lok = []
    for o in out.GetListOfKeys():
        lok.append(str(o.GetName()))
    logger.info('Writing histograms using AIDA_'+tree_name)

    do_weight_sys = True
    for name, chain in chains.items():
        if name == 'Data' and tree_name != 'nominal':
            continue
        for histn, props in hists.items():
            weight_name = 'nomWeightwLum'
            if 'Data' in name: cut = props.cut
            else: cut = str(lumi)+'*'+weight_name+'*'+props.cut
            hname = tree_name+'_'+name.split('_')[0]+'_'+histn
            if hname in lok:
                logger.warning(hname+' Already in output file')
                continue
            h = tree2hist(chain,hname,props.binning,props.var,cut,overflow=True)
            h.Write()
            if tree_name == 'nominal' and 'Data' not in name and do_weight_sys:
                for systW in _systematic_weights:
                    for ud in systW:
                        cut = str(lumi)+'*'+ud+'*'+props.cut
                        hname = tree_name+'_'+name.split('_')[0]+'_'+histn+'_'+ud.split('wLum_')[-1]
                        h = tree2hist(chain,hname,props.binning,props.var,cut,overflow=True)
                        h.Write()
    out.Close()
    return True

def total_systematic_histogram(root_file, hist_name=None,
                               proc_names=['ttbar','Wt','WW','Ztautaujets','Diboson','Fakes'],
                               return_stat_error=False):
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
    #if 'AIDA_nominal' not in root_file.GetListOfKeys():
    #    logger.error('Have to have the nominal histograms')
    #    exit()
    nominals   = { pname : root_file.Get('nominal_'+pname+'_'+hist_name)
                   for pname in proc_names }
    nominals   = { pname : hist2array(h,return_edges=True, return_err=True)
                   for pname, h in nominals.items() }
    edges      = nominals['ttbar'][1][0]
    nbins      = len(nominals['ttbar'][0])
    total_band = np.zeros(nbins,dtype=np.float32)
    nom_h      = np.zeros(nbins,dtype=np.float32)
    nom_stater = np.zeros(nbins,dtype=np.float32)
    for pname, nom in nominals.items():
        nom_h      = nom_h + nom[0]
        if return_stat_error:
            nom_stater = nom_stater + nom[2]*nom[2]
    for pname in proc_names:
        proc_nom = nominals[pname][0]
        # the two sided systematics in trees
        for ud in _systematic_ud_prefixes:
            if 'MET_Soft' in ud: updown = ['Up','Down'] # why does MET use different name... lame
            else:                updown = ['__1up','__1down']
            hname_up   = ud+updown[0]+'_'+pname+'_'+hist_name
            hname_down = ud+updown[1]+'_'+pname+'_'+hist_name
            if hname_up not in root_file.GetListOfKeys():
                logger.warning(hname+' systematic not available for process '+pname+'!')
                continue
            if hname_down not in root_file.GetListOfKeys():
                logger.warning(hname+' systematic not available for process '+pname+'!')
                continue
            arr_up     = hist2array(root_file.Get(hname_up))
            arr_down   = hist2array(root_file.Get(hname_down))
            total_band = total_band + (0.5*(arr_up-arr_down))*(0.5*(arr_up-arr_down))
        # the one sided systematics in trees, symmetrize it
        for osed in _systematic_singles:
            hname = osed+'_'+pname+'_'+hist_name
            if hname not in root_file.GetListOfKeys():
                logger.warning(hname+' systematic not available!')
                continue
            arr        = hist2array(root_file.Get(hname))
            total_band = total_band + (proc_nom-arr)*(proc_nom-arr)
        # the hists from weights
        for wud in _systematic_weights:
            u_ws, d_ws = wud[0].split('wLum_')[-1], wud[1].split('wLum_')[-1]
            arr_up     = hist2array(root_file.Get('nominal_'+pname+'_'+hist_name+'_'+u_ws))
            arr_down   = hist2array(root_file.Get('nominal_'+pname+'_'+hist_name+'_'+d_ws))
            total_band = total_band + (0.5*(arr_up-arr_down))*(0.5*(arr_up-arr_down))
        # lumi uncertainty on fixed backgrounds
        if pname == 'Diboson' or pname == 'RareSM' or pname == 'Fakes' or pname == 'Wt':
            total_band = total_band + (0.0374*proc_nom)*(0.0374*proc_nom)
    # root that summed quadrature.
    total_band = np.sqrt(total_band)

    if return_stat_error:
        nom_stater = np.sqrt(nom_stater)
        return nom_h, total_band, edges, nom_stater
    return nom_h, total_band, edges
