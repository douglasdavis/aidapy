# -*- coding: utf-8 -*-

from __future__ import print_function

import math
import yaml
import numpy as np
import ROOT

import logging
from .. import configure_logging
configure_logging()
logger  = logging.getLogger('aidapy')

from .utils import array2hist
from .utils import hist2array
from .utils import shift_overflow
from .utils import tree2hist
from .utils import fast2full

from aidapy.meta import _systematic_trees
from aidapy.meta import _systematic_weights
from aidapy.meta import _systematic_singles
from aidapy.meta import _systematic_ud_prefixes

def _unravel_dsids(arr):
    dsids = []
    for entry in arr:
        if isinstance(entry,list):
            for dsid in range(entry[0],entry[1]+1):
                dsids.append(dsid)
        else:
            dsids.append(entry)
    return dsids

def _root_file_dict(yaml_file):
    """
    Build based on new production YAML file
    """
    with open(yaml_file) as f:
        files_from_yaml = yaml.load(f)
    file_dict = {}
    file_dict['Fakes_FULL_main'] = ['nominal',[]]
    for process, vals1 in files_from_yaml.items():
        for simtype, vals2 in vals1.items():
            for samptype, vals3 in vals2.items():
                aidaTreeName = vals3['OutTreeName']
                DSIDs = _unravel_dsids(vals3['DSIDs'])
                procsimsamp = '_'.join([process,simtype,samptype])
                file_dict[procsimsamp] = [aidaTreeName,[]]
                files = ['_'.join([process,str(dsid)])+'.root' for dsid in DSIDs]
                if 'FULL_main' in procsimsamp:
                    file_dict['Fakes_FULL_main'][1] += files
                file_dict[procsimsamp][1] += files
    return file_dict

def generate_mc_hists(mc_prod_yaml_file, hist_yaml, mc_prefix='', aida_tree='nominal', lumi=36.1,
                      ignore=['Zll_FULL_main','Wjets_FULL_main'], output='out.root', Z_genWeights=False,
                      provide_file_dict=None, do_fast2full=True):
    """
    Create MC histograms from two YAML config files.

    Parameters
    ----------
    mc_prod_yaml_file: str
      Path to YAML file which organizes MC files
    hist_yaml: str
      Path to YAML file which defines the desired histograms
    mc_prefix: str
      The path to where MC files exist
    aida_tree: str
      Which AIDA tree to use to build the histograms
    lumi: float
      What luminosity to scale to
    ignore: list
      Different process prefixes (defined in the MC YAML file) to ignore
    output: str
      Path and name of output ROOT file
    Z_genWeights: bool
      Build histograms using the generator weights available in Ztautau
    do_fast2full: bool
      Do Fast to Full histograms (try scale fast sim hists to appropriate "full" hists).
      Only for nominal trees.
    """
    # provide file dict to not rebuild if it exists somewhere.
    if provide_file_dict is not None:
        file_dict = provide_file_dict
    else:
        file_dict = _root_file_dict(mc_prod_yaml_file)

    chains = {}
    for fde, fdk in file_dict.items():
        ckey, tname = fde, fdk[0]
        if 'fast' in tname and aida_tree != 'nominal':
            continue
        if 'Fakes' in fde:
            chains[ckey] = ROOT.TChain('AIDAfk_'+aida_tree)
            [chains[ckey].Add(mc_prefix+'/'+f) for f in fdk[1]]
        else:
            if aida_tree == 'nominal':
                chains[ckey] = ROOT.TChain('AIDA_'+tname)
            else:
                chains[ckey] = ROOT.TChain('AIDA_'+aida_tree)
            [chains[ckey].Add(mc_prefix+'/'+f) for f in fdk[1]]
    for ig in ignore:
        if ig in chains:
            del chains[ig]

    with open(hist_yaml) as hf:
        hist_dict = yaml.load(hf)

    output_file = ROOT.TFile(output,'UPDATE')
    rootkeys    = [str(o.GetName()) for o in output_file.GetListOfKeys()]
    for pname, chain in chains.items():
        if 'main' not in pname and aida_tree != 'nominal':
            continue
        for hist_name, hist_props in hist_dict.items():
            hname  = pname+'_'+aida_tree+'_'+hist_name
            if hname in rootkeys:
                logger.warning(hname+' already in file')
            else:
                cut = str(lumi)+'*nomWeightwLum*('+hist_props['cut']+')'
                h = tree2hist(chain,hname,hist_props['bins'],hist_props['var'],cut,True,True)
                logger.info(h)
                h.Write()
            if aida_tree == 'nominal' and 'FAST' not in pname:
                for systW in _systematic_weights:
                    for ud in systW[:-1]:
                        hname = pname+'_'+aida_tree+'_'+hist_name+'_'+ud
                        if hname in rootkeys:
                            logger.warning(hname+' already in file')
                        else:
                            cut = str(lumi)+'*'+ud+'*('+hist_props['cut']+')'
                            h = tree2hist(chain,hname,hist_props['bins'],hist_props['var'],cut,True,True)
                            logger.info(h)
                            h.Write()
            if aida_tree == 'nominal' and 'Ztautau' in pname and Z_genWeights:
                for i in range(1,115):
                    hname = pname+'_'+aida_tree+'_'+hist_name+'_genWeight'+str(i)
                    if hname in rootkeys:
                        logger.warning(hname+' already in file')
                    else:
                        cut = str(lumi)+'*weightSyswLum_genWeight'+str(i)+'*('+hist_props['cut']+')'
                        h = tree2hist(chain,hname,hist_props['bins'],hist_props['var'],cut,True,True)
                        logger.info(h)
                        h.Write()
    output_file.Close()

    ## Reopen the output file and lets try to make some systematic
    ## histograms from the fastsim samples.  This is hard coded naming
    ## based on YAML naming defined in the template.
    if aida_tree == 'nominal' and do_fast2full:

        def check_and_write(h, keys):
            """
            Check if a histogram name is in a list of keys from a file,
            if so shoot a warning, if not, shoot info and write the hist.
            """
            if str(h.GetName()) in keys:
                logger.warning(str(h.GetName()+' already in file'))
            else:
                logger.info(h)
                h.Write()

        output_file = ROOT.TFile(output,'UPDATE')
        listofkeys  = [str(o.GetName()) for o in output_file.GetListOfKeys()]

        for hist_name in hist_dict:
            hn = hist_name

            ########################################################
            #### First ttbar #######################################
            ########################################################
            pnom, edges, perr = hist2array(output_file.Get('ttbar_FULL_main_nominal_'+hn),
                                           return_edges=True, return_err=True)
            edges = edges[0]
            bins = (pnom.size,edges[0],edges[-1])
            fast_nom, fast_nom_e = hist2array(output_file.Get('ttbar_FAST_main_nominal_'+hn),
                                              return_err=True)

            ## additonal radiation
            if 'ttbar_FAST_sysARup_nominal_'+hn in listofkeys \
               and 'ttbar_FAST_sysARdown_nominal_'+hn in listofkeys:
                h = fast2full(output_file,'ttbar_FAST_sysARup_nominal_'+hn,
                              'ttbar_FULL_sysARup_nominal_'+hn,fast_nom,pnom,fast_nom_e,perr,bins)
                check_and_write(h,listofkeys)
                h = fast2full(output_file,'ttbar_FAST_sysARdown_nominal_'+hn,
                              'ttbar_FULL_sysARdown_nominal_'+hn,fast_nom,pnom,fast_nom_e,perr,bins)
                check_and_write(h,listofkeys)
            else:
                logger.warning('Cannot find ttbar additional radiation FAST hists')

            ## factorization/hadronization
            if 'ttbar_FAST_sysFH_nominal_'+hn in listofkeys:
                h = fast2full(output_file,'ttbar_FAST_sysFH_nominal_'+hn,'ttbar_FULL_sysFH_nominal_'+hn,
                              fast_nom,pnom,fast_nom_e,perr,bins)
                check_and_write(h,listofkeys)
            else:
                logger.warning('Cannot find ttbar factorization/hadronization FAST hists')

            ## hard scattering
            if 'ttbar_FAST_sysHS_nominal_'+hn in listofkeys:
                h = fast2full(output_file,'ttbar_FAST_sysHS_nominal_'+hn,'ttbar_FULL_sysHS_nominal_'+hn,
                              fast_nom,pnom,fast_nom_e,perr,bins)
                check_and_write(h,listofkeys)
            else:
                logger.warning('Cannot find ttbar hard scattering FAST hists')
            ########################################################
            ########################################################

            ########################################################
            #### Now Wt ############################################
            ########################################################
            pnom,perr = hist2array(output_file.Get('Wt_FULL_main_nominal_'+hn),return_err=True)
            fast_nom,fast_nom_e = hist2array(output_file.Get('Wt_FAST_main_nominal_'+hn),
                                              return_err=True)

            ## additional radiation
            if 'Wt_FAST_sysARup_nominal_'+hn in listofkeys \
               and 'Wt_FAST_sysARdown_nominal_'+hn in listofkeys:
                h = fast2full(output_file,'Wt_FAST_sysARup_nominal_'+hn,'Wt_FULL_sysARup_nominal_'+hn,
                              fast_nom,pnom,fast_nom_e,perr,bins)
                check_and_write(h,listofkeys)
                h = fast2full(output_file,'Wt_FAST_sysARdown_nominal_'+hn,'Wt_FULL_sysARdown_nominal_'+hn,
                              fast_nom,pnom,fast_nom_e,perr,bins)
                check_and_write(h,listofkeys)
            else:
                logger.warning('Cannot find Wt addiational radiation FAST histograms')

            ## factorization/hadrontization
            if 'Wt_FAST_sysFH_nominal_'+hn in listofkeys:
                h = fast2full(output_file,'Wt_FAST_sysFH_nominal_'+hn,'Wt_FULL_sysFH_nominal_'+hn,
                              fast_nom,pnom,fast_nom_e,perr,bins)
                check_and_write(h,listofkeys)
            else:
                logger.warning('Cannot find Wt factorization/hadronization FAST hists')

            ## hard scattering
            if 'Wt_FAST_sysHS1_nominal_'+hn in listofkeys \
               and 'Wt_FAST_sysHS2_nominal_'+hn in listofkeys:
                h = fast2full(output_file,'Wt_FAST_sysHS1_nominal_'+hn,'Wt_FULL_sysHS1_nominal_'+hn,
                              fast_nom,pnom,fast_nom_e,perr,bins)
                check_and_write(h,listofkeys)
                h = fast2full(output_file,'Wt_FAST_sysHS2_nominal_'+hn,'Wt_FULL_sysHS2_nominal_'+hn,
                              fast_nom,pnom,fast_nom_e,perr,bins)
                check_and_write(h,listofkeys)
            else:
                logger.warning('Cannot find Wt hard scattering FAST hists')
            ########################################################
            ########################################################

        ### Finally close up the output file.
        output_file.Close()


def generate_data_hists(data_root_file, hist_yaml, output='out.root'):
    """
    Using the histogram YAML config and a single ROOT file containing
    an AIDA ntuple of data, build histograms.

    Parameters
    ----------
    data_root_file: ROOT.TFile
      ROOT file containing AIDA ntuple
    hist_yaml: str
      Path to a YAML file which defines the desired histograms
    output: str
      Path and name of output ROOT file
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
            h   = tree2hist(chain,hname,hist_props['bins'],hist_props['var'],cut,True,True)
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
    yaml_config: str
      Path to the YAML config file
    output: str
      Name of output ROOT file
    systematics: str or list
      Which systematic trees to process. If not 'ALL', provide a list
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


def total_systematic_histogram(root_file, hist_name=None,
                               proc_names=['ttbar','Wt','WW','Ztautau','Diboson','Fakes'],
                               return_stat_error=False, do_gen_weights=False):
    """
    A function to calculate and return a histogram with a total
    systematic error band in numpy format.

    Parameters
    ----------
    root_file: ROOT.TFile
      The ROOT file with the histograms
    hist_name: str
      The name of the histogram to generate the band for (must exist in ROOT file!)
    proc_names: str
      The names of the processes contributing to the band (must exist in ROOT file!)

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
    listofkeys = root_file.GetListOfKeys()
    nominals   = { pname : root_file.Get(pname+'_FULL_main_nominal_'+hist_name)
                   for pname in proc_names }
    nominals   = { pname : hist2array(h,return_edges=True, return_err=True)
                   for pname, h in nominals.items() }
    edges      = nominals['ttbar'][1][0]
    nbins      = len(nominals['ttbar'][0])
    total_band = np.zeros(nbins,dtype=np.float32)
    nom_h      = np.zeros(nbins,dtype=np.float32)
    nom_stater = np.zeros(nbins,dtype=np.float32)
    for pname, nom in nominals.items():
        nom_h = nom_h + nom[0]
        if return_stat_error:
            nom_stater = nom_stater + nom[2]*nom[2]
    for pname in proc_names:
        pnom = nominals[pname][0]
        # the two sided systematics in trees
        for ud in _systematic_ud_prefixes:
            if 'MET_Soft' in ud[0]: updown = ['Up','Down'] # why does MET use different name... lame
            else:                updown = ['__1up','__1down']
            hname_up   = pname+'_FULL_main_'+ud[0]+updown[0]+'_'+hist_name
            hname_down = pname+'_FULL_main_'+ud[0]+updown[1]+'_'+hist_name
            if hname_up not in listofkeys:
                logger.warning(hname_up+' systematic not available for process '+pname+'!')
                continue
            if hname_down not in listofkeys:
                logger.warning(hname_down+' systematic not available for process '+pname+'!')
                continue
            arr_up      = hist2array(root_file.Get(hname_up))
            arr_down    = hist2array(root_file.Get(hname_down))
            total_band += (0.5*(arr_up-arr_down))*(0.5*(arr_up-arr_down))
        # the one sided systematics in trees, symmetrize it
        for osed in _systematic_singles:
            hname = pname+'_FULL_main_'+osed[0]+'_'+hist_name
            if hname not in listofkeys:
                logger.warning(hname+' systematic not available!')
                continue
            arr         = hist2array(root_file.Get(hname))
            total_band += (pnom-arr)*(pnom-arr)
        # the hists from weights
        for wud in _systematic_weights:
            u_ws, d_ws  = wud[0].split('wLum_')[-1], wud[1].split('wLum_')[-1]
            arr_up   = hist2array(root_file.Get(pname+'_FULL_main_nominal_'+hist_name+'_weightSyswLum_'+u_ws))
            arr_down = hist2array(root_file.Get(pname+'_FULL_main_nominal_'+hist_name+'_weightSyswLum_'+d_ws))
            total_band +=(0.5*(arr_up-arr_down))*(0.5*(arr_up-arr_down))
        # Ztautau generator weights
        if 'Ztautau' in pname and do_gen_weights:
            for i in range(1,115): ## all 115 explode the sys band. need to look into this
                hname = pname+'_FULL_main_'+hist_name+'_genWeight'+str(i)
                if hname not in listofkeys:
                    logger.warning(hname+' systematic not available for process '+pname+'!')
                    continue
                arr         = hist2array(root_file.Get(hname))
                total_band += (pnom-arr)*(pnom-arr)
        # lumi uncertainty on fixed backgrounds
        if pname == 'Diboson' or pname == 'RareSM' or pname == 'Fakes':
            total_band += (0.0374*pnom)*(0.0374*pnom)
        # ttbar modeling uncertainties
        if pname == 'ttbar' and ('ttbar_FULL_main_nominal_'+hist_name) in listofkeys:
            if ('ttbar_FULL_sysARup_nominal_'+hist_name) in listofkeys \
               and('ttbar_FULL_sysARdown_nominal_'+hist_name) in listofkeys:
                full_ARU    = hist2array(root_file.Get('ttbar_FULL_sysARup_nominal_'+hist_name))
                full_ARD    = hist2array(root_file.Get('ttbar_FULL_sysARdown_nominal_'+hist_name))
                total_band += np.power(0.5*(full_ARU-full_ARD),2)
            else:
                logger.warning('ttbar additional radiation sys histograms not present')
            if ('ttbar_FULL_sysFH_nominal_'+hist_name) in listofkeys:
                full_FH     = hist2array(root_file.Get('ttbar_FULL_sysFH_nominal_'+hist_name))
                total_band += np.power(pnom-full_FH,2)
            else:
                logger.warning('ttbar hadronization sys histograms not present')
            if ('ttbar_FULL_sysHS_nominal_'+hist_name) in listofkeys:
                full_HS     = hist2array(root_file.Get('ttbar_FULL_sysHS_nominal_'+hist_name))
                total_band += np.power(pnom-full_HS,2)
            else:
                logger.warning('ttbar hard scattering sys histograms not present')
        elif pname == 'ttbar':
            logger.warning('Cannot add ttbar modeling systematics to band')
        else:
            pass
        # Wt modeling uncertainties
        if pname == 'Wt' and ('Wt_FULL_main_nominal_'+hist_name) in listofkeys:
            if ('Wt_FULL_sysARup_nominal_'+hist_name) in listofkeys \
               and ('Wt_FULL_sysARdown_nominal_'+hist_name) in listofkeys:
                full_ARU    = hist2array(root_file.Get('Wt_FULL_sysARup_nominal_'+hist_name))
                full_ARD    = hist2array(root_file.Get('Wt_FULL_sysARdown_nominal_'+hist_name))
                total_band += np.power(0.5*(full_ARU-full_ARD),2)
            else:
                logger.warning('Wt additional radiation sys histograms not present')
            if ('Wt_FULL_sysFH_nominal_'+hist_name) in listofkeys:
                full_FH     = hist2array(root_file.Get('Wt_FULL_sysFH_nominal_'+hist_name))
                total_band += np.power(pnom-full_FH,2)
            else:
                logger.warning('Wt hadronization sys histograms not present')
            if ('Wt_FULL_sysHS1_nominal_'+hist_name) in listofkeys \
               and ('Wt_FULL_sysHS2_nominal_'+hist_name) in listofkeys:
                full_HS1    = hist2array(root_file.Get('Wt_FULL_sysHS1_nominal_'+hist_name))
                full_HS2    = hist2array(root_file.Get('Wt_FULL_sysHS2_nominal_'+hist_name))
                total_band += np.power(full_HS1-full_HS2,2)
            else:
                logger.warning('Wt hard scattering sys histograms not present')
            if ('Wt_FULL_sysDS_nominal_'+hist_name) in listofkeys:
                full_DS     = hist2array(root_file.Get('Wt_FULL_sysDS_nominal_'+hist_name))
                total_band += np.power(full_DS-pnom,2)
        elif pname == 'Wt':
            logger.warning('Cannot add Wt modeling systematics to band')
        else:
            pass

    # root that summed quadrature.
    total_band = np.sqrt(total_band)

    if return_stat_error:
        nom_stater = np.sqrt(nom_stater)
        return nom_h, total_band, edges, nom_stater
    return nom_h, total_band, edges
