# -*- coding: utf-8 -*-
"""
Help handling ATLAS dataset IDs
"""

import ROOT

_dsid_table = {
    'ttbar_PowPy8'     : [410501] ,
    'ttbar_PowPy8_dil' : [410503] ,
    'ttbar_PowPy6'     : [410000] ,
    'Wt_PowPy6'        : [410015,410016] ,
    'Zjets_S21'        : [i for i in range(361372,361444)] ,
    'Zjets_S22'        : [i for i in range(363361,363411)] + [i for i in range(363102,363123)] ,
    'Zjets_S221'       : [i for i in range(364100,364142)] ,
    'Wjets_S22'        : [i for i in range(363436,363484)] + [i for i in range(363331,363354)] ,
    'Wjets_S221'       : [i for i in range(364156,364198)] ,
    'Diboson_PowPy8'   : [361601,361603,361607] , #[361610,361604]
    'WW_PowPy8'        : [361600, 361606] ,
    "WW_dedicated"     : [361600, 361078] ,
    "Diboson_dedicated": [361601, 361607, 361603, 361604, 361610]
}

def get_proc_gen(dsid):
    """
    Given a DSID, get the initial state (process) and generator in the
    form [process]_[generator]. The available combinations are listed
    in the get_dsids function documentation.

    Parameters
    ----------
    dsid : self evident

    Returns
    -------
    k : str
        the [process]_[generator] string

    """
    for k, v in _dsid_table.items():
        if dsid in v:
            return k
    return 'Unknown'

def get_dsids(key):
    """
    Get a list of DSIDs associated with a
    process and its generator

    Available process+generator keys:
    ttbar_PowPy8,
    ttbar_PowPy8_dil,
    ttbar_PowPy6,
    Wt_PowPy6,
    Zjets_S21,
    Zjets_S22,
    Zjets_S221,
    Wjets_S22,
    Wjets_S221,
    Diboson_PowPy8,
    WW_PowPy8,
    
    Parameters
    ----------
    key : the string (available listed above)

    Returns
    -------
    list
        List of DSIDs associated with the key
    """
    if key not in _dsid_table:
        raise ValueError(str(key)+' not Available')
    else:
        return _dsid_table[key]

def proc_gen_from_file(rootfile):
    """
    A function to return the initial state (process) and
    generator associated with a ROOT file.

    Parameters
    ----------
    rootfile : path to ROOT file _or_ the ROOT file itself

    Returns
    -------
    str
      [process]_[generator]

    """
    if isinstance(rootfile, ROOT.TFile):
        pass
    elif isinstance(rootfile, str):
        rootfile = ROOT.TFile(rootfile)
    else:
        raise TypeError('Must be ROOT file or path to ROOT file')
    t = rootfile.Get('AIDA_meta')
    t.GetEntry(0)
    d = int(t.dsid)
    if d == 0:
        return 'Data'
    return get_proc_gen(d)

def sort_files_from_txt(txtfile, procs_and_gens):
    """
    Sort files into a dictionary based on initial state (process) and
    generator.

    Parameters
    ----------
    txtfile : plain text file listing the full path of all the files to sort
    procs_and_gens : list of [process]_[generator] strings you'd like in
      the final dictionary

    Returns
    -------
    dict
      Dictionary of all processes and the respective files
    """
    retdic = { pandg : [] for pandg in procs_and_gens }
    with open(txtfile) as f:
        for line in f:
            l = line.rstrip()
            p_gen = proc_gen_from_file(l)
            if p_gen in retdic:
                retdic[p_gen].append(l)
    return retdic

_systematic_weights = [
    [ 'weightSyswLum_jvt_UP'                        , 'weightSyswLum_jvt_DOWN'                         ] ,
    [ 'weightSyswLum_leptonSF_EL_SF_ID_UP'          , 'weightSyswLum_leptonSF_EL_SF_ID_DOWN'           ] ,
    [ 'weightSyswLum_leptonSF_EL_SF_Isol_UP'        , 'weightSyswLum_leptonSF_EL_SF_Isol_DOWN'         ] ,
    [ 'weightSyswLum_leptonSF_EL_SF_Reco_UP'        , 'weightSyswLum_leptonSF_EL_SF_Reco_DOWN'         ] ,
    [ 'weightSyswLum_leptonSF_EL_SF_Trigger_UP'     , 'weightSyswLum_leptonSF_EL_SF_Trigger_DOWN'      ] ,
    [ 'weightSyswLum_leptonSF_MU_SF_ID_STAT_UP'     , 'weightSyswLum_leptonSF_MU_SF_ID_STAT_DOWN'      ] ,
    [ 'weightSyswLum_leptonSF_MU_SF_ID_SYST_UP'     , 'weightSyswLum_leptonSF_MU_SF_ID_SYST_DOWN'      ] ,
    [ 'weightSyswLum_leptonSF_MU_SF_Isol_STAT_UP'   , 'weightSyswLum_leptonSF_MU_SF_Isol_STAT_DOWN'    ] ,
    [ 'weightSyswLum_leptonSF_MU_SF_Isol_SYST_UP'   , 'weightSyswLum_leptonSF_MU_SF_Isol_SYST_DOWN'    ] ,
    [ 'weightSyswLum_leptonSF_MU_SF_Trigger_STAT_UP', 'weightSyswLum_leptonSF_MU_SF_Trigger_STAT_DOWN' ] ,
    [ 'weightSyswLum_leptonSF_MU_SF_Trigger_SYST_UP', 'weightSyswLum_leptonSF_MU_SF_Trigger_SYST_DOWN' ] ,
    [ 'weightSyswLum_pileup_UP'                     , 'weightSyswLum_pileup_DOWN'                      ] ,
]

_systematic_trees = [
    'EG_RESOLUTION_ALL__1down',
    'EG_RESOLUTION_ALL__1up',
    'EG_SCALE_ALL__1down',
    'EG_SCALE_ALL__1up',
    'JET_21NP_JET_BJES_Response__1down',
    'JET_21NP_JET_BJES_Response__1up',
    'JET_21NP_JET_EffectiveNP_1__1down',
    'JET_21NP_JET_EffectiveNP_1__1up',
    'JET_21NP_JET_EffectiveNP_2__1down',
    'JET_21NP_JET_EffectiveNP_2__1up',
    'JET_21NP_JET_EffectiveNP_3__1down',
    'JET_21NP_JET_EffectiveNP_3__1up',
    'JET_21NP_JET_EffectiveNP_4__1down',
    'JET_21NP_JET_EffectiveNP_4__1up',
    'JET_21NP_JET_EffectiveNP_5__1down',
    'JET_21NP_JET_EffectiveNP_5__1up',
    'JET_21NP_JET_EffectiveNP_6__1down',
    'JET_21NP_JET_EffectiveNP_6__1up',
    'JET_21NP_JET_EffectiveNP_7__1down',
    'JET_21NP_JET_EffectiveNP_7__1up',
    'JET_21NP_JET_EffectiveNP_8restTerm__1down',
    'JET_21NP_JET_EffectiveNP_8restTerm__1up',
    'JET_21NP_JET_EtaIntercalibration_Modelling__1down',
    'JET_21NP_JET_EtaIntercalibration_Modelling__1up',
    'JET_21NP_JET_EtaIntercalibration_NonClosure__1down',
    'JET_21NP_JET_EtaIntercalibration_NonClosure__1up',
    'JET_21NP_JET_EtaIntercalibration_TotalStat__1down',
    'JET_21NP_JET_EtaIntercalibration_TotalStat__1up',
    'JET_21NP_JET_Flavor_Composition__1down',
    'JET_21NP_JET_Flavor_Composition__1up',
    'JET_21NP_JET_Flavor_Response__1down',
    'JET_21NP_JET_Flavor_Response__1up',
    'JET_21NP_JET_Pileup_OffsetMu__1down',
    'JET_21NP_JET_Pileup_OffsetMu__1up',
    'JET_21NP_JET_Pileup_OffsetNPV__1down',
    'JET_21NP_JET_Pileup_OffsetNPV__1up',
    'JET_21NP_JET_Pileup_PtTerm__1down',
    'JET_21NP_JET_Pileup_PtTerm__1up',
    'JET_21NP_JET_Pileup_RhoTopology__1down',
    'JET_21NP_JET_Pileup_RhoTopology__1up',
    'JET_21NP_JET_PunchThrough_MC15__1down',
    'JET_21NP_JET_PunchThrough_MC15__1up',
    'JET_21NP_JET_SingleParticle_HighPt__1down',
    'JET_21NP_JET_SingleParticle_HighPt__1up',
    'JET_JER_SINGLE_NP__1up',
    'MET_SoftTrk_ResoPara',
    'MET_SoftTrk_ResoPerp',
    'MET_SoftTrk_ScaleDown',
    'MET_SoftTrk_ScaleUp',
    'MUON_ID__1down',
    'MUON_ID__1up',
    'MUON_MS__1down',
    'MUON_MS__1up',
    'MUON_SAGITTA_RESBIAS__1down',
    'MUON_SAGITTA_RESBIAS__1up',
    'MUON_SAGITTA_RHO__1down',
    'MUON_SAGITTA_RHO__1up',
    'MUON_SCALE__1down',
    'MUON_SCALE__1up',
]

_systematic_ud_prefixes = [ 'EG_RESOLUTION_ALL',
                            'EG_SCALE_ALL',
                            'JET_21NP_JET_BJES_Response',
                            'JET_21NP_JET_EffectiveNP_1',
                            'JET_21NP_JET_EffectiveNP_2',
                            'JET_21NP_JET_EffectiveNP_3',
                            'JET_21NP_JET_EffectiveNP_4',
                            'JET_21NP_JET_EffectiveNP_5',
                            'JET_21NP_JET_EffectiveNP_6',
                            'JET_21NP_JET_EffectiveNP_7',
                            'JET_21NP_JET_EffectiveNP_8restTerm',
                            'JET_21NP_JET_EtaIntercalibration_Modelling',
                            'JET_21NP_JET_EtaIntercalibration_NonClosure',
                            'JET_21NP_JET_EtaIntercalibration_TotalStat',
                            'JET_21NP_JET_Flavor_Composition',
                            'JET_21NP_JET_Flavor_Response',
                            'JET_21NP_JET_Pileup_OffsetMu',
                            'JET_21NP_JET_Pileup_OffsetNPV',
                            'JET_21NP_JET_Pileup_PtTerm',
                            'JET_21NP_JET_Pileup_RhoTopology',
                            'JET_21NP_JET_PunchThrough_MC15',
                            'JET_21NP_JET_SingleParticle_HighPt',
                            'MUON_ID',
                            'MUON_MS',
                            'MUON_SAGITTA_RESBIAS',
                            'MUON_SAGITTA_RHO',
                            'MUON_SCALE',
                            'MET_SoftTrk_Scale',
                            'MET_SoftTrk_Scale'
]

_systematic_singles = [
    'JET_JER_SINGLE_NP__1up',
    'MET_SoftTrk_ResoPara',
    'MET_SoftTrk_ResoPerp',
]
