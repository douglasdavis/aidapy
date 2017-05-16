import ROOT

meas = ROOT.RooStats.HistFactory.Measurement("meas","meas")
meas.SetOutputFilePrefix("./results/aidaFit")
meas.SetExportOnly(False)
meas.SetPOI("mu_TTBAR")
#meas.SetPOI("mu_ZTAUTAU")
#meas.SetPOI("mu_WT")
#meas.AddConstanstParam("Lumi")
#meas.AddConstanstParam("alpha_syst1")
#meas.AddConstantParam("alpha_ttbar_AR")
#meas.AddConstantParam("alpha_Wt_AR")
#meas.AddConstantParam("alpha_Ztautau_JFR")
root_file = "/Users/ddavis/Software/aidapy/aida_histograms.root"

meas.SetLumi(1.0)
meas.SetLumiRelErr(0.03)

chan = ROOT.RooStats.HistFactory.Channel("1pj")
chan.SetData("Data_met_1pj",root_file)

ttbar = ROOT.RooStats.HistFactory.Sample("ttbar_met_1pj","ttbar_FULL_main_nominal_met_1pj",root_file)
#ttbar.AddHistoSys("ttbar_AR","ttbar_FULL_sysARdown_nominal_met_1pj",root_file,"","ttbar_FULL_sysARup_nominal_met_1pj",root_file,"")
ttbar.AddNormFactor("mu_TTBAR",1,0,3)
chan.AddSample(ttbar)

Wt = ROOT.RooStats.HistFactory.Sample("Wt_met_1pj","Wt_FULL_main_nominal_met_1pj",root_file)
#Wt.AddHistoSys("Wt_AR","Wt_FULL_sysARdown_nominal_met_1pj",root_file,"","Wt_FULL_sysARup_nominal_met_1pj",root_file,"")
#Wt.AddNormFactor("mu_WT",1,0,3)
chan.AddSample(Wt)

Ztautau = ROOT.RooStats.HistFactory.Sample("Ztautau_met_1pj","Ztautau_FULL_main_nominal_met_1pj",root_file)
#Ztautau.AddHistoSys("Ztautau_JFR",
#                    "Ztautau_FULL_main_JET_21NP_JET_Flavor_Response__1down_met_1pj",root_file,"",
#                    "Ztautau_FULL_main_JET_21NP_JET_Flavor_Response__1up_met_1pj",  root_file,"")
#Ztautau.AddNormFactor("mu_ZTAUTAU",1,0,3)
chan.AddSample(Ztautau)
WW = ROOT.RooStats.HistFactory.Sample("WW_met_1pj","WW_FULL_main_nominal_met_1pj",root_file)
chan.AddSample(WW)
Diboson = ROOT.RooStats.HistFactory.Sample("Diboson_met_1pj","Diboson_FULL_main_nominal_met_1pj",root_file)
chan.AddSample(Diboson)
Fakes = ROOT.RooStats.HistFactory.Sample("Fakes_met_1pj","Fakes_FULL_main_nominal_met_1pj",root_file)
chan.AddSample(Fakes)
RareSM = ROOT.RooStats.HistFactory.Sample("RareSM_met_1pj","RareSM_FULL_main_nominal_met_1pj",root_file)
chan.AddSample(RareSM)

meas.AddChannel(chan)
meas.CollectHistograms()
meas.PrintTree()
#meas.PrintXML("xmlFromPy", meas.GetOutputFilePrefix());
x = ROOT.RooStats.HistFactory.MakeModelAndMeasurementFast(meas)

pass
