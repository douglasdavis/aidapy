import ROOT
ratioline = ROOT.TF1('ratioline','1',-14000.0,14000.0)
ratioline.SetLineWidth(1)
ratioline.SetLineStyle(7)
ratioline.SetLineColor(1)
atlaslabel = ROOT.TLatex()
atlaslabel.SetNDC()
atlaslabel.SetTextFont(73)
atlaslabel.SetTextSize(14)
atlaslabelText = ROOT.TLatex()
atlaslabelText.SetNDC()
atlaslabelText.SetTextFont(43)
atlaslabelText.SetTextSize(14)
aidalabel = ROOT.TLatex()
aidalabel.SetNDC()
aidalabel.SetTextFont(43)
aidalabel.SetTextSize(12)
ROOT.gROOT.ProcessLine('TGaxis::SetMaxDigits(4)')
def format_legend(legend):
    legend.SetTextFont(43)
    legend.SetTextSize(12)
    legend.SetFillStyle(0)
    legend.SetBorderSize(0)
def styling():
    aida_style = ROOT.TStyle('aida_style','aida_style')
    icol=0
    aida_style.SetFrameBorderMode(icol)
    aida_style.SetFrameFillColor(icol)
    aida_style.SetCanvasBorderMode(icol)
    aida_style.SetCanvasColor(icol)
    aida_style.SetPadBorderMode(icol)
    aida_style.SetPadColor(icol)
    aida_style.SetStatColor(icol)
    aida_style.SetPadTopMargin(0.05)
    aida_style.SetPadRightMargin(0.05)
    aida_style.SetPadBottomMargin(0.1)
    aida_style.SetPadLeftMargin(0.16)
    
    aida_style.SetTitleXOffset(2.0)
    aida_style.SetTitleYOffset(1.85)
    aida_style.SetTextFont(16)
    aida_style.SetTextSize(14)
    aida_style.SetLabelFont(43,'x')
    aida_style.SetTitleFont(43,'x')
    aida_style.SetLabelFont(43,'y')
    aida_style.SetTitleFont(43,'y')
    aida_style.SetLabelFont(43,'z')
    aida_style.SetTitleFont(43,'z')
    aida_style.SetLabelSize(13,'x')
    aida_style.SetTitleSize(14,'x')
    aida_style.SetLabelSize(13,'y')
    aida_style.SetTitleSize(14,'y')
    aida_style.SetLabelSize(13,'z')
    aida_style.SetTitleSize(14,'z')
    aida_style.SetMarkerStyle(8)
    aida_style.SetMarkerSize(.75)
    aida_style.SetHistLineWidth(1)
    aida_style.SetLineStyleString(2,'[12 12]')
    aida_style.SetEndErrorSize(0.0)
    
    aida_style.SetOptTitle(0)
    aida_style.SetOptStat(0)
    aida_style.SetOptFit(0)
    aida_style.SetPadTickX(1)
    aida_style.SetPadTickY(1)
    aida_style.cd()
    ROOT.gROOT.ForceStyle()
def pad_margining(pad1,pad2):
    pad1.SetBottomMargin(0.0275)
    pad1.SetTopMargin(0.0685)
    pad1.SetRightMargin(.0255)
    pad2.SetTopMargin(0.015)
    pad2.SetRightMargin(.0255)
    pad2.SetBottomMargin(0.40)
    pad2.SetFrameFillColor(0)
    pad2.SetFrameBorderMode(0)
def hist_formatting(chist,isdata=False,logging=False):
    chist.SetMarkerStyle(8)
    chist.SetMarkerSize(.75)
    chist.GetXaxis().SetLabelOffset(99)
    chist.GetXaxis().SetTitleOffset(99)
    if isdata:
        chist.SetLineWidth(1)
        chist.SetMaximum(chist.GetMaximum()*1.4)
        if logging:
            chist.SetMaximum(chist.GetMaximum()*15)
            chist.SetMinimum(10.0)
        chist.GetYaxis().SetTickLength(0.02)
styling()
class stackedHistogram(object):
    def __init__(self,plotName,histograms,data,ratio,mc_colors,lcols=[1 for _ in range(7)],
                 xtitle='X title',ytitle='Y title',ratiotitle='Data/MC',outdir='.',lumi='XX',logging=False):
        self.plotName   = plotName
        self.histograms = histograms
        self.data       = data
        self.data.SetMaximum(self.data.GetMaximum()*1.3)
        self.ratio      = ratio
        self.ratio.SetMaximum(1.5)
        self.ratio.SetMinimum(0.5)
        self.ratiotitle = ratiotitle
        self.ratio.GetXaxis().SetTitleOffset(4.20)
        self.xtitle     = xtitle
        self.ytitle     = ytitle
        self.stack = ROOT.THStack(plotName+'_stack',plotName+'_stack')
        self.outdir = outdir
        for histogram, color, lcolor in zip(self.histograms,mc_colors,lcols):
            histogram.SetFillColor(color)
            hist_formatting(histogram)
            if color == ROOT.kWhite:
                histogram.SetLineColor(ROOT.kBlack)
            else:
                histogram.SetLineColor(color)
                histogram.SetLineColor(ROOT.kBlack)
            histogram.SetLineColor(lcolor)
            if 'zz' in histogram.GetName():
                histogram.SetLineColor(color)
            self.stack.Add(histogram)
        hist_formatting(data,isdata=True,logging=logging)
        self.lumi = lumi
    def draw(self,manualmax=False,xtitle='xtitle',yunit='',logscale=False,njetbins=False):
        self.data.SetTitle(';;Events/'+str(round(self.ratio.GetXaxis().GetBinWidth(1),2))+' '+yunit)
        self.ratio.SetTitle(';'+xtitle+';'+self.ratiotitle)
        self.ratio.GetYaxis().SetNdivisions(5)
        if manualmax is not False:
            self.data.SetMaximum(manualmax)
        if not logscale:
            self.data.SetMinimum(0.)
        self.canvas = ROOT.TCanvas(self.plotName,self.plotName,450,475)
        self.pad0   = ROOT.TPad(self.plotName+'_pad0',self.plotName+'_pad0',0.0,0.28,0.95,0.95)
        self.pad1   = ROOT.TPad(self.plotName+'_pad1',self.plotName+'_pad1',0.0,0.00,0.95,0.27)
        if logscale:
            self.pad0.SetLogy()
        pad_margining(self.pad0,self.pad1)
        #proctitles = ['t#bar{t}','Z+jets','WW','Wt','WZ','ZZ']
        proctitles = ['t#bar{t}','Z+jets','Wt','WW','Fakes','WZ/ZZ']
        legend = ROOT.TLegend(.815,.585,1.025,.90)
        format_legend(legend)
        legend.AddEntry(self.data,'Data','p')
        hcutlist = [h for h in list(reversed(self.histograms))]
        #hcutlist.append(self.histograms[2])
        #hcutlist.append(self.histograms[0])
        for hist, pt in zip(hcutlist,proctitles):
            legend.AddEntry(hist,pt,'f')
        if njetbins:
            self.data.SetMaximum(self.data.GetMaximum()*20)
            nbins = self.data.GetXaxis().GetNbins()
            labels = [str(i) for i in range(nbins-1)]
            labels.append('#geq '+str(nbins-1))
            #print labels
            for i,lab in enumerate(labels):
                self.ratio.GetXaxis().SetBinLabel(i+1,lab)
        self.pad0.cd()
        self.data.Draw('e')
        self.stack.Draw('same,hist')
        self.data.Draw('e,same')
        legend.Draw('same')
        atlaslabel.DrawLatex(.1875,.865,'ATLAS')
        atlaslabelText.DrawLatex(.1875+.11,.865,'Internal')
        aidalabel.DrawLatex(.1875,.82,'#sqrt{s} = 13 TeV, '+self.lumi+' fb^{-1}')
        self.pad1.cd()
        self.ratio.GetYaxis().CenterTitle()
        self.ratio.Draw('e')
        ratioline.Draw('same')
        self.canvas.cd()
        self.pad0.Draw()
        self.pad1.Draw()
        self.pad0.RedrawAxis()
        self.pad1.RedrawAxis()
        #self.canvas.SaveAs(self.outdir+'/'+self.plotName+'.eps')
        self.canvas.SaveAs(self.outdir+'/'+self.plotName+'.pdf')
class compareHists(object):
    def __init__(self,plotName,histogram0,histogram1,label0,label1,color0,color1,
                 xtitle='X title',ytitle='Y title',ratiotitle='hist0/hist1',outdir='.'):
        self.plotName = plotName
        self.hist0    = histogram0
        self.hist1    = histogram1
        self.ratio    = self.hist0.Clone()
        self.ratio.Divide(self.hist1)
        self.ratio.GetXaxis().SetTitleOffset(4.20)
        self.xtitle   = xtitle
        self.ytitle   = ytitle
        hist_formatting(self.hist0)
        hist_formatting(self.hist1)
        self.hist0.SetMaximum(self.hist0.GetMaximum()*1.3)
        self.hist1.SetMaximum(self.hist1.GetMaximum()*1.3)
        self.hist0.SetLineColor(color0)
        self.hist1.SetLineColor(color1)
        self.hist0.SetFillColor(color0)
        self.hist1.SetFillColor(color1)
        self.hist0.SetMarkerColor(color0)
        self.hist1.SetMarkerColor(color1)
        self.labels     = [label0,label1]
        self.ratiotitle = ratiotitle
        self.hist0.SetTitle(';;'+self.ytitle)
        self.hist1.SetTitle(';;'+self.ytitle)
        self.outdir = outdir
        
    def draw(self,manualmax=False,manualmin=False,custombinlabels=None):
        self.ratio.SetTitle(';'+self.xtitle+';'+self.ratiotitle)
        self.ratio.GetYaxis().SetNdivisions(5)
        if manualmax is not False:
            self.hist0.SetMaximum(manualmax)
            self.hist1.SetMaximum(manualmax)
        if manualmin is not False:
            self.hist0.SetMinimum(manualmin)
            self.hist1.SetMinimum(manualmin)
        if custombinlabels is not None:
            for i, cbl in enumerate(custombinlabels):
                self.ratio.GetXaxis().SetBinLabel(i+1,cbl)
            
        self.canvas = ROOT.TCanvas(self.plotName,self.plotName,520,375)
        self.pad0   = ROOT.TPad(self.plotName+'_pad0',self.plotName+'_pad0',0.0,0.31,0.95,0.95)
        self.pad1   = ROOT.TPad(self.plotName+'_pad1',self.plotName+'_pad1',0.0,0.00,0.95,0.30)
        pad_margining(self.pad0,self.pad1)
        legend = ROOT.TLegend(.765,.79,0.975,.89)
        format_legend(legend)
        legend.AddEntry(self.hist0,self.labels[0],'p')
        legend.AddEntry(self.hist1,self.labels[1],'p')
        
        self.pad0.cd()
        self.hist0.Draw('e')
        self.hist1.Draw('e,same')
        legend.Draw('same')
        atlaslabel.DrawLatex(.1775,.855,'ATLAS')
        atlaslabelText.DrawLatex(.1775+.1,.855,'Internal')
        aidalabel.DrawMathText(.1775,.795,aidatext)
        
        self.pad1.cd()
        self.ratio.Draw('e')
        ratioline.Draw('same')
        self.canvas.cd()
        self.pad0.Draw()
        self.pad1.Draw()
        self.pad0.RedrawAxis()
        self.pad1.RedrawAxis()
        self.canvas.SaveAs(self.outdir+'/'+self.plotName+'.eps')
        self.canvas.SaveAs(self.outdir+'/'+self.plotName+'.pdf')
        ROOT.SetOwnership(self.pad0,False)
        ROOT.SetOwnership(self.pad1,False)
        ROOT.SetOwnership(self.canvas,False)
