#!/usr/bin/env python

def split4fit(infile, histogram_list=['met_0j','met_1pj']):
    """
    Split the main histogram file into a number of files based on the
    x-axis of the histograms. You can put all met_0j histograms into a
    single file and all met_1j1b histograms into a single file.

    Parameters
    ----------
    infile: str
      path to ROOT file containing the entire set of histograms created by aida.py
    histogram_list: list
      Each entry in this list will correspond to an ouput file containing
      histograms of this variable from all states/samples 
    """
    import ROOT

    outpfx = infile.split('.root')[0]
    if '/' in outpfx:
        outpfx = outpfx.split('/')[-1]
    infile = ROOT.TFile(infile,'read')
    lok     = [str(o.GetName()) for o in infile.GetListOfKeys()]

    def make_a_file(hist_name):
        thishist = [k for k in lok if (hist_name in k)]
        new_thishist_hists = {}
        thishist_file  = ROOT.TFile(outpfx+'_'+hist_name+'.root','RECREATE')
        for k in thishist:
            cloned_list = k.split('_'+hist_name)
            cloned_name = cloned_list[0].replace('_nominal','')
            if 'weightSys' in cloned_list[1]:
                cloned_name = cloned_name+cloned_list[1]
            #print(cloned_name)
            new_thishist_hists[cloned_name] = infile.Get(k).Clone(cloned_name)
            new_thishist_hists[cloned_name].SetDirectory(thishist_file)
        thishist_file.Write()
        thishist_file.Close()

    for h in histogram_list:
        make_a_file(h)
