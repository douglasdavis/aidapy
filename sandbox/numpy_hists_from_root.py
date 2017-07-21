from root_numpy import root2array
import matplotlib.pyplot as plt
import numpy as np
import aidapy.hist as aph
import ROOT

file_list = ["/Users/ddavis/Software/LocalData/outs/Wt_410015.root",
             "/Users/ddavis/Software/LocalData/outs/Wt_410016.root"]

r2a = root2array(file_list,"AIDA_nominal").view(np.recarray)

cut = 'elmu&&!SS&&njets==1&&nbjets==1'
s1  = aph.np_selection(r2a,cut)

n, bins, err = aph.np_hist(r2a,'met',(20,0,200),s1,'nomWeightwLum')
plt.errorbar(aph.bin_centers(bins),n,yerr=err,fmt='o')
plt.show()

h = aph.array2hist(n, 'aname', (len(bins)-1,bins[0],bins[-1]), err)

f = ROOT.TFile('testfile.root','recreate')
h.SetDirectory(f)
f.Write()
f.Close()
