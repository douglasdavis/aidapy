from __future__ import print_function
import aidapy.meta as am
import ROOT
HF = ROOT.RooStats.HistFactory
RF = ROOT.RooFit

rootFile = "/Users/ddavis/Software/aidapy/aida_histograms.root"

meas = HF.Measurement("measurement","measurement")
meas.SetOutputFilePrefix("./out5/plss")
meas.AddPOI("mu_TTBAR")
meas.AddPOI("mu_WW")
meas.AddPOI("mu_ZTAUTAU")
meas.AddConstantParam("Lumi")

meas.SetLumi(1.0)
meas.SetLumiRelErr(0.04)
meas.SetExportOnly(False)

def setup_channel(name):
    chan = HF.Channel(name)
    chan.SetData("Data_"+name,rootFile)
    samples = {}
    samples["ttbar"]   = HF.Sample("ttbar",  "ttbar_FULL_main_nominal_"+name,  rootFile,"")
    samples["WW"]      = HF.Sample("WW",     "WW_FULL_main_nominal_"+name,     rootFile,"")
    samples["Ztautau"] = HF.Sample("Ztautau","Ztautau_FULL_main_nominal_"+name,rootFile,"")
    for sample in samples:
        samples[sample].AddNormFactor("mu_"+sample.upper(),1.0,0.1,2.5)
    samples["Wt"]      = HF.Sample("Wt",     "Wt_FULL_main_nominal_"+name,     rootFile,"")
    samples["Diboson"] = HF.Sample("Diboson","Diboson_FULL_main_nominal_"+name,rootFile,"")
    samples["Fakes"]   = HF.Sample("Fakes",  "Fakes_FULL_main_nominal_"+name,  rootFile,"")
    samples["RareSM"]  = HF.Sample("RareSM", "RareSM_FULL_main_nominal_"+name, rootFile,"")

    for treesys in am._systematic_ud_prefixes:
        downsfx = "__1down"
        upsfx   = "__1up"
        if 'MET' in treesys:
            downsfx = "Down"
            upsfx   = "Up"
        for iproc in ["ttbar","WW","Ztautau","Wt","Diboson","Fakes","RareSM"]:
            samples[iproc].AddHistoSys(treesys,
                                       iproc+"_FULL_main_"+treesys+downsfx+"_"+name,rootFile,"",
                                       iproc+"_FULL_main_"+treesys+upsfx+  "_"+name,rootFile,"")

    samples["ttbar"].AddHistoSys("ttbar_AR",
                                 "ttbar_FULL_sysARdown_nominal_"+name,rootFile,"",
                                 "ttbar_FULL_sysARup_nominal_"+name,  rootFile,"")

    chan.AddSample(samples["ttbar"])
    chan.AddSample(samples["WW"])
    chan.AddSample(samples["Ztautau"])
    chan.AddSample(samples["Wt"])
    chan.AddSample(samples["Diboson"])
    chan.AddSample(samples["Fakes"])
    chan.AddSample(samples["RareSM"])

    return chan

channel_names = ["met_0j","met_1pj"]
for chan in channel_names:
    c = setup_channel(chan)
    meas.AddChannel(c)

#meas.AddChannel(channel)
meas.CollectHistograms()
meas.PrintTree()
RF.NumCPU(4)
ws = HF.MakeModelAndMeasurementFast(meas)
exit(0)
