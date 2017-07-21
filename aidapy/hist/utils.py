import numpy as np
import ROOT
import math

def bin_centers(arr):
    """
    Get the middle values of an array of bin edges

    Parameters
    ----------
    arr: numpy.ndarray
         The array of bin edges

    Returns
    -------
    numpy.ndarray
         The array of centers
    """
    return (np.delete(arr,[0])-(np.ediff1d(arr)/2.0))


def hist2array(hist, include_overflow=False, copy=True, return_edges=False, return_err=False):
    """
    This algorithm is Copyright (c) 2012-2017, The root_numpy developers
    See disclaimer here: https://github.com/scikit-hep/root_numpy/blob/master/LICENSE

    This function is an incomplete clone of root_numpy.hist2array for 1D histograms
    https://github.com/scikit-hep/root_numpy/blob/master/root_numpy/_hist.py

    Parameters
    ----------
    hist: ROOT.TH1
        The ROOT histogram to convert
    include_overflow: bool, optional (default=False)
        If true, the over and underflow bins will be part of the array
    copy: bool, optional (default=True)
        If true copy the underlying array to own its memory
    return_edges: bool, optional (default=False)
        If true, return bin edges
    return_err: bool, optional (default=False)
        If true, return the sqrt(sum(weights squared))

    Returns
    -------
    numpy.ndarray
        NumPy array with bin heights
    list(numpy.ndarray)
        A list of arrays. One for each axis' bin edges
    numpy.ndarray
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

def array2hist(array, hist_name='hist_name', binning=(10,0,100), errors=None):
    """
    Create a ROOT histogram from a numpy array.

    Parameters
    ----------
    array: np.ndarray
      numpy array where the elements are bin heights
    hist_name: str
      name for ROOT histogram
    binning: tuple
      binning for ROOT histogram

    Returns
    -------
    ROOT.TH1
      a ROOT TH1F or TH1D (dependent on the array dtype)
    """
    if array.size != binning[0]:
        raise ValueError('Array size must be number of bins!')
    padded = np.pad(array,(1,1),'constant')
    if array.dtype == np.float32:
        h = ROOT.TH1F(hist_name,hist_name,binning[0],binning[1],binning[2])
    elif array.dtype == np.float64:
        h = ROOT.TH1D(hist_name,hist_name,binning[0],binning[1],binning[2])
    else:
        raise TypeError('We can only handle np.float32 and np.float64')
    h.Set(padded.size, padded)
    h.SetEntries(array.size)
    if errors is not None:
        if errors.size != array.size:
            raise ValueError('Error is not the same size as the array')
        pe = np.pad(np.ascontiguousarray(errors, dtype=np.float64), (1,1), 'constant')
        h.SetError(pe)
    return h

def shift_overflow(hist):
    """
    A function to shift the overflow bin in a ROOT
    histogram into the last bin. Only supports 1D histograms.

    Parameters
    ----------
    hist: ROOT.TH1
      The ROOT histogram
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

def tree2hist(tree, hist_name, binning, var, cut, overflow=False, negatives_to_zero=False):
    """
    A function to create a histogram using TTree::Draw()

    Parameters
    ----------
    tree: ROOT.TTree or ROOT.TChain
      The ROOT tree or chain
    hist_name: str
      The name-in-memory of the histogram to be created
    binning: tuple
      The binning of the histogram (nbins,xmin,xmax)
    var: str
      The variable (branch name) in the tree to histogram
    cut: str
      The selection string handed to TTree::Draw
    overflow: bool
      Shift the overflow bin the the last real bin
    negatives_to_zero:
      Make negative valued bins zero.
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
    if negatives_to_zero:
        for idx in (np.where(hist2array(hist) < 0)[0]):
            hist.SetBinContent(int(idx)+1,0.0)
    return hist

def fast2full(root_file, faststr, fullstr, fast_nom, pnom, fast_nom_e, pnom_err, bins):
    """
    This function does the fast to full histogram scaling.  Error is
    assigned using standard error propagation.. since the error is
    just statistical. The new "FULL" histogram is written to the tree.

    Parameters
    ----------
    root_file: ROOT.TFile
        The ROOT file for all of our histograms
    faststr: str
        The string label of the fast sim systematic histogram already in the output file
    fullstr: str
        The new string label for the "full" sim systematic histogram to be stored
    fast_nom: numpy.ndarray
        An array of bin heights for the fast sim nominal histogram
    pnom: numpy.ndarray
        The processes full sim nominal histogram bin heights
    fast_nom_e: numpy.ndarray
        The statistical uncertainty in each bin (fast sim nominal)
    pnom_err: numpy.ndarray
        The statistical uncertainty in each bin (full sim nominal)
    bin: tuple
        The number of bins, left edge, and right edge (nbins,xmin,xmax)

    Returns
    -------
    ROOT.TH1
        "Full Sim" ROOT histogram associated with the original fast sim histogram.
    """
    fast_a, err  = hist2array(root_file.Get(faststr), return_err=True)
    full_a       = (pnom/fast_nom)*fast_a
    full_e_term  = np.power(fast_a/fast_nom*pnom_err,2)
    full_e_term += np.power(pnom/fast_nom*err,2)
    full_e_term += np.power(pnom*fast_a/(fast_nom*fast_nom)*fast_nom_e,2)
    full_h       = array2hist(full_a, fullstr, bins, errors=np.sqrt(full_e_term))
    return full_h

def np_selection(x, tcut):
    """
    Parse a ROOT TCut style string and construct a
    numpy array for selection (numpy array of bools)

    Parameters
    ----------
    x: np.array
        The numpy array for the set of events
    tcut: str
        The ROOT style TCut. This is a limited cut
        that can only interpret "&&" combinations.

    Returns
    -------
    np.array
        The selection array of bools
    """
    if not isinstance(x,np.ndarray):
        raise TypeError('x must be a numpy array!')
    if not isinstance(tcut,str):
        raise TypeError('cuts must be a string!')
    cuts = tcut.split(tcut[tcut.find('&&')])
    while '' in cuts:
        cuts.remove('')

    sel = np.array([True for _ in range(x.shape[0])])
    for c in cuts:
        if '==' in c:
            cc = c.split('==')
            sel = (sel)&(getattr(x,cc[0])==float(cc[1]))
        elif '!=' in c:
            cc = c.split('!=')
            sel = (sel)&(getattr(x,cc[0])!=float(cc[1]))
        elif '>=' in c:
            cc = c.split('>=')
            sel = (sel)&(getattr(x,cc[0])>=float(cc[1]))
        elif '<=' in c:
            cc = c.split('<=')
            sel = (sel)&(getattr(x,cc[0])<=float(cc[1]))
        elif '!' in c:
            cc = c.split('!')
            sel = (sel)&(getattr(x,cc[1])==False)
        else:
            sel = (sel)&(getattr(x,c)==True)
    return sel

def np_hist(dataset, var, binning, selection, weight, lumi=36.1, shift_overflow=True):
    """
    Create a histogram from purely numpy stored event data

    Parameters
    ----------
    dataset: numpy.ndarray (recarray)
        The numpy recarray for the dataset
    var: str
        The variable name that we're histogramming
    binning: tuple
        A tuple of (nbins, xmin, xmax)
    selection: np.ndarray (of bools)
        A numpy array of bools for event selection
    weight: str
        The weight variable in the dataset to use
    lumi: float
        The luminosity to scale to
    shift_overflow: bool
        Bring the overflow into the last real bin.

    Returns
    -------
    numpy.ndarray
        The bin heights
    numpy.ndarray
        The bin edges
    numpy.ndarray
        The statistical error in each bin
    """
    x = getattr(dataset,var)[selection]
    w = getattr(dataset,weight)[selection]
    bins = np.linspace(binning[1],binning[2],binning[0]+1)
    ofbs = np.array([binning[2],1.0e6],dtype=np.float32)

    h, bins = np.histogram(x,bins=bins,weights=w*lumi)
    of, trh = np.histogram(x,bins=ofbs,weights=w*lumi)
    h[-1] += of[0]

    digitized = np.digitize(x,bins)
    digiti_of = np.digitize(x,ofbs)
    bin_sumw2 = np.zeros(binning[0])
    for i in range(1,binning[0]+1):
        bin_sumw2[i-1] = sum(np.power(w[np.where(digitized==i)[0]],2))
    bin_sumw2[-1] += sum(np.power(w[np.where(digiti_of==1)[0]],2))
    err = np.sqrt(bin_sumw2)
    return h, bins, err
