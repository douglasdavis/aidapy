from aidapy.hist import total_systematic_histogram
from aidapy.hist import hist2array

import numpy as np

import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.ticker import AutoMinorLocator, MultipleLocator
from style_mpl import style_mpl
import matplotlib as mpl
import matplotlib.gridspec as gsc
plt.style.use('classic')
from pylab import setp
for key, val in style_mpl().iteritems():
    mpl.rcParams[key] = val
from matplotlib.font_manager import FontProperties
fontBase  = FontProperties()
fontATLAS = fontBase.copy()
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

def hplot_mpl(root_file, hist_name='met_1pj', xtitle='', ytitle='',logy=False,
              proc_names=['Wt','ttbar','Fakes','WW','Diboson','Ztautaujets','RareSM']):
    nominals = { pname : root_file.Get('nominal_'+pname+'_'+hist_name) for pname in proc_names }
    nominals = { pname : hist2array(h,return_edges=True) for pname, h in nominals.iteritems() }
    data     = root_file.Get('nominal_Data_'+hist_name)
    data     = hist2array(data)
    nom_h, total_band, edges, staterr = total_systematic_histogram(root_file,hist_name,proc_names,
                                                                   return_stat_error=True)
    centers  = np.delete(edges,[0])-(np.ediff1d(edges)/2.0)
    to_stack = [nominals[name][0] for name in ['RareSM','Diboson','Fakes','WW','Wt','Ztautaujets','ttbar']]
    cols     = ['brown','black','gray','green','blue','orange','white']
    fig,ax,axerr = canvas_with_ratio()
    ax.errorbar(centers,data,yerr=np.sqrt(data),fmt='ko',label=r'$\mathrm{Data}$')
    ax.hist([centers for _ in to_stack],weights=to_stack,bins=edges,stacked=True,
            color=cols,histtype='stepfilled',
            label=[r'Rare SM',r'Diboson',r'Fake/NP (MC)',
                   r'WW',r'Wt',r'$Z\rightarrow\tau\tau$',r'$t\bar{t}$'])
    #ax.errorbar(centers,nom_h,yerr=total_band,fmt='ro')
    syspatches = []
    syspatches = [patches.Rectangle((c-w/2,v-err),w,err*2,hatch='\\\\\\\\',fill=False,edgecolor='none')
                  for c, v, err, w in zip(centers,nom_h,total_band,np.ediff1d(edges))]
    for p in syspatches: ax.add_patch(p)
    trashpatch = patches.Rectangle((0,0),0,0,hatch='\\\\\\\\',fill=False,edgecolor='none',
                                   label=r'Systematics')
    ax.add_patch(trashpatch)
    ax.errorbar(centers,data,yerr=np.sqrt(data),fmt='ko')
    ax.legend(numpoints=1)
    ax.set_ylim([0,np.max(data)*1.3])
    ax.text(.05,.92,'ATLAS',transform=ax.transAxes,style='oblique',size=16,fontproperties=fontATLAS)
    ax.text(.175,.92,r'Internal, AIDA OS $e\mu$, pre-fit',transform=ax.transAxes,size=16)
    ax.text(.05,.835,r'$\sqrt{s}$ = 13 TeV, $\int \mathcal{L}$dt = 36.1 fb$^{-1}$',
            transform=ax.transAxes,size=16)
    ax.text(.05,.75,'',transform=ax.transAxes,size=16)
    domcErr = np.sqrt(1.0/(nom_h*nom_h)*data + data*data*staterr*staterr/(nom_h*nom_h*nom_h*nom_h))
    axerr.errorbar(centers,data/nom_h,yerr=domcErr,fmt='ko')#data/(nom_h*nom_h)*total_band
    errpatches = []
    errpatches = [patches.Rectangle((c-w/2,1-err),w,err*2,hatch='\\\\\\\\',fill=False,edgecolor='none')
                  for c, v, err, w in zip(centers,data/nom_h,data/(nom_h*nom_h)*total_band,np.ediff1d(edges))]
    for p in errpatches: axerr.add_patch(p)
    axerr.set_ylim([0.5,1.5])
    axerr.set_xlim([edges[0],edges[-1]])
    axerr.plot(edges,np.array([1 for _ in edges]),'k-')
    if 'met' in hist_name:
        xpref = r'$E_\mathrm{T}^\mathrm{miss}$ [GeV]'
    elif 'llpT' in hist_name:
        xpref = r'Leading Lepton $p_\mathrm{T}$ [GeV]'
    elif 'mu' in hist_name:
        xpref = r'Muon $p_\mathrm{T}$ [GeV]'
    elif 'el' in hist_name:
        xpref = r'Electron $p_\mathrm{T}$ [GeV]'
    else:
        xpref = r''
    if '_all' in hist_name:
        xsuf = r''
    elif '_0j' in hist_name:
        xsuf = r'$(N_\mathrm{jets} = 0)$'
    elif '_1pj' in hist_name:
        xsuf = r'$(N_\mathrm{jets} \geq 1)$'
    else:
        xsuf = ''
    xtitle = xpref+' '+xsuf
    if 'pT' in hist_name:
        logy = True
    axerr.set_xlabel(xtitle)
    ax.set_ylabel(ytitle)
    if logy: ax.set_yscale('log'), ax.set_ylim([np.min(data)*.01,np.max(data)*500])
    fig.savefig(hist_name+'.pdf')
    #plt.show()
