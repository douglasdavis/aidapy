# -*- coding: utf-8 -*-
"""
Help handling ATLAS dataset IDs
"""

_dsid_table = {
    "ttbar_PowPy8"     : [410501] ,
    "ttbar_PowPy8_dil" : [410503] ,
    "ttbar_PowPy6"     : [410000] ,
    "Wt_PowPy6"        : [410015,410016] ,
    "Zjets_S21"        : [i for i in range(361372,361444)] ,
    "Zjets_S22"        : [i for i in range(363361,363411)] + [i for i in range(363102,363123)] ,
    "Zjets_S221"       : [i for i in range(364100,364142)] ,
    "Wjets_S22"        : [i for i in range(363436,363484)] + [i for i in range(363331,363354)] ,
    "Wjets_S221"       : [i for i in range(364156,364198)] ,
    "Diboson_PowPy8"   : [361601, 361603, 361604, 361607, 361609, 361610, 361611] ,
    "WW_PowPy8"        : [361600, 361606]
}

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
        raise ValueError(str(key)+" not Available")
    else:
        return _dsid_table[key]
