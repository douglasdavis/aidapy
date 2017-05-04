# -*- coding: utf-8 -*-
"""
Handling AIDA histograms
"""

from __future__ import print_function

import json
import math
from collections import namedtuple
import yaml

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
        hist = ROOT.TH1F(hist_name,hist_name,binning[0],binning[1],binning[2])
        return hist

    tree.Draw(var+'>>'+hist_name+bin_str, cut, 'goff')
    hist = ROOT.gDirectory.Get(str(hist_name))
    if overflow:
        shift_overflow(hist)
    return hist


def _root_file_dict(yaml_file):
    """
    Build a dictionary of ROOT files using a YAML config.
    The Fakes_FULL_main entry will be filled with the
    contents of all other FULL_main entries
    """
    with open(yaml_file) as f:
        files_from_yaml = yaml.load(f)

    file_dict = {}
    file_dict['Fakes_FULL_main'] = []
    for process, vals1 in files_from_yaml.items():
        for simtype, vals2 in vals1.items():
            for samptype, vals3 in vals2.items():
                procsimsamp = '_'.join([process,simtype,samptype])
                file_dict[procsimsamp] = []
                for dsid, vals4 in vals3.items():
                    for entry in vals4:
                        if isinstance(entry,list):
                            for d in range(entry[0],entry[1]+1):
                                file_dict[procsimsamp].append(str(d)+'_'+simtype+'.root')
                                if 'FULL_main' in procsimsamp:
                                    file_dict['Fakes_FULL_main'].append(str(d)+'_'+simtype+'.root')
                        else:
                            file_dict[procsimsamp].append(str(entry)+'_'+simtype+'.root')
                            if 'FULL_main' in procsimsamp:
                                file_dict['Fakes_FULL_main'].append(str(entry)+'_'+simtype+'.root')
    return file_dict

def generate_mc_hists(mc_yaml_file, hist_yaml, mc_prefix='', aida_tree='nominal', lumi=36.1,
                      ignore=['Zll_FULL_main','Wjets_FULL_main'], output='out.root', Z_genWeights=False,
                      provide_file_dict=None):
    """
    Create MC histograms from two YAML config files.

    Parameters
    ----------
    mc_yaml_file: A YAML files which organizes MC files
    hist_yaml:    A YAML file which defines the desired histograms
    mc_prefix:    The path to where MC files exist
    aida_tree:    Which AIDA tree to use to build the histograms
    lumi:         What luminosity to scale to
    ignore:       Different process prefixes (defined in the MC YAML file) to ignore
    output:       Name of output ROOT file
    Z_genWeights: Build histograms using the generator weights available in Ztautau
    """

    # provide file dict to not rebuild if it exists somewhere.
    if provide_file_dict is not None:
        file_dict = provide_file_dict
    else:
        file_dict = _root_file_dict(mc_yaml_file)

    chains = { fd : ROOT.TChain('AIDA_'+aida_tree) for fd in file_dict if fd != 'Fakes_FULL_main' }
    # fakes have their own tree name.
    chains['Fakes_FULL_main'] = ROOT.TChain('AIDAfk_'+aida_tree)
    for ig in ignore:
        if ig in chains:
            del chains[ig]
    if aida_tree != 'nominal':
        dels = [c for c in chains if 'FAST' in c]
        for d in dels:
            del chains[d]
    for c in chains:
        for f in file_dict[c]:
            chains[c].Add(mc_prefix+'/'+f)

    with open(hist_yaml) as hf:
        hist_dict = yaml.load(hf)

    output_file = ROOT.TFile(output,'UPDATE')
    rootkeys    = [str(o.GetName()) for o in output_file.GetListOfKeys()]
    for pname, chain in chains.items():
        for hist_name, hist_props in hist_dict.items():
            hname  = pname+'_'+aida_tree+'_'+hist_name
            if hname in rootkeys:
                logger.warning(hname+' already in file')
            else:
                cut = str(lumi)+'*nomWeightwLum*('+hist_props['cut']+')'
                h = tree2hist(chain,hname,hist_props['bins'],hist_props['var'],cut,True)
                logger.info(h)
                h.Write()
            if aida_tree == 'nominal' and 'FAST' not in pname:
                for systW in _systematic_weights:
                    for ud in systW:
                        hname = pname+'_'+aida_tree+'_'+hist_name+'_'+ud
                        if hname in rootkeys:
                            logger.warning(hname+' already in file')
                        else:
                            cut = str(lumi)+'*'+ud+'*('+hist_props['cut']+')'
                            h = tree2hist(chain,hname,hist_props['bins'],hist_props['var'],cut,True)
                            logger.info(h)
                            h.Write()
            if aida_tree == 'nominal' and 'Ztautau' in pname and Z_genWeights:
                for i in range(1,115):
                    hname = pname+'_'+aida_tree+'_'+hist_name+'_genWeight'+str(i)
                    if hname in rootkeys:
                        logger.warning(hname+' already in file')
                    else:
                        cut = str(lumi)+'*weightSyswLum_genWeight'+str(i)+'*('+hist_props['cut']+')'
                        h = tree2hist(chain,hname,hist_props['bins'],hist_props['var'],cut,True)
                        logger.info(h)
                        h.Write()

    output_file.Close()

def generate_data_hists(data_root_file, hist_yaml, output='out.root'):
    """
    Using the histogram YAML config and a single ROOT file containing
    an AIDA ntuple of data, build histograms.

    Parameters
    ----------
    data_root_file: ROOT file containing AIDA ntuple
    hist_yaml:    A YAML file which defines the desired histograms
    output:       Name of output ROOT file
    """
    chain = ROOT.TChain('AIDA_nominal')
    chain.Add(data_root_file)
    output_file = ROOT.TFile(output,'UPDATE')
    rootkeys = [str(o.GetName()) for o in output_file.GetListOfKeys()]
    with open(hist_yaml) as hf:
        hist_dict = yaml.load(hf)
    for hist_name, hist_props in hist_dict.items():
        hname = 'Data_'+hist_name
        if hname in rootkeys:
            logger.warning(hname+' already in file')
        else:
            cut = '1.0*('+hist_props['cut']+')'
            h   = tree2hist(chain,hname,hist_props['bins'],hist_props['var'],cut,True)
            logger.info(h)
            h.Write()

    output_file.Close()


def generate_hists(yaml_config, output='out.root', systematics='ALL'):
    """
    Generate histograms based on a single YAML file.
    This is essentially a wrapper around the functions
    - generate_data_hists
    - generate_mc_hists
    steered by the config file

    Parameters
    ----------
    yaml_config: Path to the YAML config file
    output:      Name of output ROOT file
    systematics: Which systematic trees to process. If not 'ALL', provide a list
    """
    with open(yaml_config) as f:
        config = yaml.load(f)

    provided = _root_file_dict(config['mc_config'])
    generate_mc_hists(config['mc_config'],config['hist_config'],
                      mc_prefix=config['mc_prefix'], output=output,
                      provide_file_dict=provided)

    if systematics == 'ALL':
        for tn in _systematic_trees:
            generate_mc_hists(config['mc_config'],config['hist_config'], aida_tree=tn,
                              mc_prefix=config['mc_prefix'], output=output,
                              provide_file_dict=provided)
    else:
        if not isinstance(systematics,list):
            raise TypeError('systematics parameter should be a list!')
        for tn in systematics:
            generate_mc_hists(config['mc_config'],config['hist_config'], aida_tree=tn,
                              mc_prefix=config['mc_prefix'], output=output,
                              provide_file_dict=provided)

    generate_data_hists(config['data_file'], config['hist_config'],
                        output=output)











#####################################################
#####################################################
#####################################################
## OLD JSON BASED STUFF BAILING ON THIS IN THE FUTURE    
#####################################################
#####################################################
#####################################################
#####################################################
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
                pass
            else:
                h = tree2hist(chain,hname,props.binning,props.var,cut,overflow=True)
                h.Write()
            if tree_name == 'nominal' and 'Data' not in name and do_weight_sys:
                for systW in _systematic_weights:
                    for ud in systW:
                        cut = str(lumi)+'*'+ud+'*'+props.cut
                        hname = tree_name+'_'+name.split('_')[0]+'_'+histn+'_'+ud.split('wLum_')[-1]
                        if hname in lok:
                            logger.warning(hname+' Already in output file')
                            pass
                        else:
                            h = tree2hist(chain,hname,props.binning,props.var,cut,overflow=True)
                            h.Write()
            if tree_name == 'nominal' and 'Ztautau' in name and do_weight_sys:
                for i in range(1,115):
                    cut = str(lumi)+'*weightSyswLum_genWeight'+str(i)+'*'+props.cut
                    hname = tree_name+'_'+name.split('_')[0]+'_'+histn+'_genWeight'+str(i)
                    if hname in lok:
                        logger.warning(hname+' Already in output file')
                        pass
                    else:
                        h = tree2hist(chain,hname,props.binning,props.var,cut,overflow=True)
                        h.Write()

    out.Close()
    return True

def json_total_systematic_histogram(root_file, hist_name=None,
                                    proc_names=['ttbar','Wt','WW','Ztautaujets','Diboson','Fakes'],
                                    return_stat_error=False, do_gen_weights=False):
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
        # Ztautau generator weights
        if 'Ztautau' in pname and do_gen_weights:
            for i in range(1,115): ## all 115 explode the sys band. need to look into this
                hname = 'nominal_'+pname+'_'+hist_name+'_genWeight'+str(i)
                if hname not in root_file.GetListOfKeys():
                    logger.warning(hname+' systematic not available for process '+pname+'!')
                    continue
                arr        = hist2array(root_file.Get(hname))
                total_band = total_band + (proc_nom-arr)*(proc_nom-arr)
        # lumi uncertainty on fixed backgrounds
        if pname == 'Diboson' or pname == 'RareSM' or pname == 'Fakes':
            total_band = total_band + (0.0374*proc_nom)*(0.0374*proc_nom)
    # root that summed quadrature.
    total_band = np.sqrt(total_band)

    if return_stat_error:
        nom_stater = np.sqrt(nom_stater)
        return nom_h, total_band, edges, nom_stater
    return nom_h, total_band, edges
