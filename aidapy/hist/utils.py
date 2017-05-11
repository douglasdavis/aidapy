import numpy as np
import ROOT

def hist2array(hist, include_overflow=False, copy=True, return_edges=False, return_err=False):
    """
    This algorithm is Copyright (c) 2012-2017, The root_numpy developers
    See disclaimer here: https://github.com/scikit-hep/root_numpy/blob/master/LICENSE

    This function is an incomplete clone of root_numpy.hist2array for 1D histograms
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

def array2hist(array, hist_name='hist_name', binning=(10,0,100), errors=None):
    """
    Create a ROOT histogram from a numpy array.

    Parameters
    ----------
    array:     numpy array
    hist_name: name for ROOT histogram
    binning:   binning for ROOT histogram

    Returns
    -------
    hist: ROOT.TH1
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
