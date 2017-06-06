from __future__ import print_function

import aidapy.meta as am

import ROOT
HF = ROOT.RooStats.HistFactory
RF = ROOT.RooFit

rootFile = "/Users/ddavis/Software/aidapy/aida_histograms.root"
meas = HF.Measurement("measurement","measurement")
meas.SetOutputFilePrefix("./out4/plss")
meas.AddPOI("mu_TTBAR")
meas.AddPOI("mu_WW")
meas.AddPOI("mu_ZTAUTAU")
meas.AddConstantParam("Lumi")
meas.AddConstantParam("alpha_syst1")

meas.SetLumi(1.0)
meas.SetLumiRelErr(0.10)
meas.SetExportOnly(False)
channel = HF.Channel("channel")
channel.SetData("Data_met_1pj",rootFile)

samples = {}
samples["ttbar"]   = HF.Sample("ttbar",  "ttbar_FULL_main_nominal_met_1pj",  rootFile,"")
samples["WW"]      = HF.Sample("WW",     "WW_FULL_main_nominal_met_1pj",     rootFile,"")
samples["Ztautau"] = HF.Sample("Ztautau","Ztautau_FULL_main_nominal_met_1pj",rootFile,"")
for sample in samples:
    samples[sample].AddNormFactor("mu_"+sample.upper(),1.0,0.1,2.5)
#samples["ttbar"].AddNormFactor("mu_TTBAR",1.0,0.1,2.5)
#samples["WW"].AddNormFactor("mu_WW",1.0,0.1,2.5)
#samples["Ztautau"].AddNormFactor("mu_ZTAUTAU",1.0,0.1,2.5)

samples["ttbar"].AddHistoSys("ttbar_AR",
                             "ttbar_FULL_sysARdown_nominal_met_1pj",rootFile,"",
                             "ttbar_FULL_sysARup_nominal_met_1pj",  rootFile,"")

for treesys in am._systematic_ud_prefixes:
    downsfx = "__1down"
    upsfx   = "__1up"
    if 'MET' in treesys:
        downsfx = "Down"
        upsfx   = "Up"
    for iproc in ["ttbar","WW","Ztautau"]:
        samples[iproc].AddHistoSys(treesys,
                                   iproc+"_FULL_main_"+treesys+downsfx+"_met_1pj",rootFile,"",
                                   iproc+"_FULL_main_"+treesys+upsfx+  "_met_1pj",rootFile,"")

channel.AddSample(samples["ttbar"])
channel.AddSample(samples["WW"])
channel.AddSample(samples["Ztautau"])

#samples["ttbar"].AddOverallSys("syst1",0.9,1.5)
#samples["WW"].AddOverallSys("syst2",0.45,1.25)
#samples["Ztautau"].AddOverallSys("syst3",0.15,1.95)

bkg0 = HF.Sample("Wt",     "Wt_FULL_main_nominal_met_1pj",     rootFile,"")
bkg1 = HF.Sample("Diboson","Diboson_FULL_main_nominal_met_1pj",rootFile,"")
bkg2 = HF.Sample("Fakes",  "Fakes_FULL_main_nominal_met_1pj",  rootFile,"")
bkg3 = HF.Sample("RareSM", "RareSM_FULL_main_nominal_met_1pj", rootFile,"")

bkg0.ActivateStatError()
bkg1.ActivateStatError()
bkg2.ActivateStatError()
bkg3.ActivateStatError()
channel.AddSample(bkg0)
channel.AddSample(bkg1)
channel.AddSample(bkg2)
channel.AddSample(bkg3)

meas.AddChannel(channel)
meas.CollectHistograms()
meas.PrintTree()
#print(RF.NumCPU(4))
#ws = HF.MakeModelAndMeasurementFast(meas)
exit(0)
