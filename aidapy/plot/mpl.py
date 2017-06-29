import os
import shutil

from aidapy.hist import total_systematic_histogram
from aidapy.hist import hist2array
#from .style_mpl import atlas_mpl_style

import numpy as np

import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.ticker import AutoMinorLocator, MultipleLocator
import matplotlib as mpl
import matplotlib.gridspec as gsc
#plt.style.use('classic')
from pylab import setp
#sty = atlas_mpl_style()
#for key, val in sty.items():
#    mpl.rcParams[key] = val
from matplotlib.font_manager import FontProperties
fontBase  = FontProperties()
fontATLAS = fontBase.copy()
fontATLAS.set_size(16)
fontATLAS.set_style('italic')
fontATLAS.set_weight('bold')

def canvas_with_ratio(figsize=(8,7),height_ratios=[3.65,1],
                      xtitle='x title',ytitle='ytitle',ratio_title='Ratio'):
    fig = plt.figure(figsize=figsize)
    gs  = gsc.GridSpec(2,1,height_ratios=height_ratios)
    gs.update(hspace=0.075)
    ax0 = fig.add_subplot(gs[0])
    ax1 = fig.add_subplot(gs[1],sharex=ax0)
    ax0.xaxis.set_minor_locator(AutoMinorLocator())
    ax0.yaxis.set_minor_locator(AutoMinorLocator())
    setp(ax0.get_xticklabels(),visible=False)
    ax0.set_ylabel(ytitle)
    ax1.set_ylabel(ratio_title)
    ax1.set_xlabel(xtitle)
    return fig, ax0, ax1

def hplot_mpl(root_file, hist_name='met_1pj', outdir='outs', xtitle='', ytitle='',logy=False,
              proc_names=['Wt','ttbar','Fakes','WW','Diboson','Ztautau','RareSM']):
    if os.path.exists(outdir):
        pass
    else:
        os.makedirs(outdir)
    nominals = { pname : root_file.Get(pname+'_FULL_main_nominal_'+hist_name) for pname in proc_names }
    nominals = { pname : hist2array(h,return_edges=True) for pname, h in nominals.items() }
    data     = root_file.Get('Data_'+hist_name)
    data     = hist2array(data)
    nom_h, total_band, edges, staterr = total_systematic_histogram(root_file,hist_name,proc_names,
                                                                   return_stat_error=True)
    centers  = np.delete(edges,[0])-(np.ediff1d(edges)/2.0)

    to_stack = [nominals[name][0] for name in ['RareSM','Diboson','Fakes','WW','Wt','Ztautau','ttbar']]
    cols     = ['darkred','black','gray','green','blue','orange','white']
    labels   = [r'Rare SM',r'Diboson',r'Fake/NP (MC)',r'WW',r'Wt',r'$Z\rightarrow\tau\tau$',r'$t\bar{t}$']
    #to_stack = [nominals[name][0] for name in ['RareSM','Diboson','Fakes','WW','Ztautau','ttbar','Wt']]
    #cols     = ['darkred','black','gray','green','orange','white','blue']
    #labels   = [r'Rare SM',r'Diboson',r'Fake/NP (MC)',r'WW',r'$Z\rightarrow\tau\tau$',r'$t\bar{t}$',r'Wt']

    fig,ax,axerr = canvas_with_ratio()
    ax.errorbar(centers,data,yerr=np.sqrt(data),fmt='ko',label=r'Data')
    ax.hist([centers for _ in to_stack],weights=to_stack,bins=edges,stacked=True,
            color=cols,histtype='stepfilled',label=labels, ls='solid', lw=1, edgecolor='black')
    syspatches = []
    syspatches = [patches.Rectangle((c-w/2,v-err),w,err*2,hatch='\\\\\\\\',fill=False,edgecolor='none')
                  for c, v, err, w in zip(centers,nom_h,total_band,np.ediff1d(edges))]
    for p in syspatches: ax.add_patch(p)
    trashpatch = patches.Rectangle((0,0),0,0,hatch='\\\\\\\\',fill=False,edgecolor='none',
                                   label=r'Systematics')
    ax.add_patch(trashpatch)
    ax.errorbar(centers,data,yerr=np.sqrt(data),fmt='ko')
    ax.legend(loc='upper right')
    l_handles, l_labels = ax.get_legend_handles_labels()
    l_handles = [l_handles[-1]] + l_handles[:-1]
    l_labels  = [l_labels[-1]]  + l_labels[:-1]
    ax.legend(l_handles,l_labels,loc='upper right',fontsize=12)
    ax.set_ylim([0,np.max(data)*1.3])
    ax.text(.05,.92,'ATLAS',transform=ax.transAxes,style='oblique',size=14,fontproperties=fontATLAS)
    ax.text(.185,.92,r'Internal, AIDA OS $e\mu$, pre-fit',transform=ax.transAxes,size=14)
    ax.text(.05,.845,r'$\sqrt{s}$ = 13 TeV, $\int \mathcal{L}$dt = 36.1 fb$^{-1}$',
            transform=ax.transAxes,size=14)
    ax.text(.05,.75,'',transform=ax.transAxes,size=14)
    domcErr = np.sqrt(1.0/(nom_h*nom_h)*data + data*data*staterr*staterr/(nom_h*nom_h*nom_h*nom_h))
    axerr.errorbar(centers,data/nom_h,yerr=domcErr,fmt='ko')#data/(nom_h*nom_h)*total_band
    errpatches = []
    errpatches = [patches.Rectangle((c-w/2,1-err),w,err*2,hatch='\\\\\\\\',fill=False,edgecolor='none')
                  for c, v, err, w in zip(centers,data/nom_h,data/(nom_h*nom_h)*total_band,np.ediff1d(edges))]
    for p in errpatches: axerr.add_patch(p)
    axerr.set_ylim([0.5,1.5])
    axerr.set_xlim([edges[0],edges[-1]])
    axerr.plot(edges,np.array([1 for _ in edges]),'k-')
    log_axes = ['pT','_2bins','_3bins']
    if any(term in hist_name for term in log_axes):
        logy = True
    axerr.set_xlabel(xtitle,fontsize=14)
    if 'njets' in hist_name:
        axerr.xaxis.set_ticks(np.array([i for i in centers]))
        newxticklabels = [str(int(i)) for i in centers]
        newxticklabels[-1] = r'$\geq '+str(int(centers[-1]))+'$'
        axerr.set_xticklabels(newxticklabels)
    ax.set_ylabel(ytitle,fontsize=14)
    if logy: ax.set_yscale('log'), ax.set_ylim([np.min(data)*.01,np.max(data)*500])
    fig.savefig(outdir+'/'+hist_name+'.pdf')
    fig.savefig(outdir+'/'+hist_name+'.png')
    #plt.show()
