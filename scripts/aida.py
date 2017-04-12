#!/usr/bin/env python

import sys, os
AIDAPYDIR = str(os.environ.get('AIDAPYDIR'))
print AIDAPYDIR
import argparse
parser = argparse.ArgumentParser(
    description='AIDA histogramming and plotting'
)
parser.add_argument('-g','--generate-histograms',action='store_true',dest='g',default=False)
parser.add_argument('-j','--json',type=str,dest='j',default=AIDAPYDIR+'/dukeatl.json')
parser.add_argument('-t','--tests',action='store_true',dest='t',default=False)
args = parser.parse_args()

import logging
logging.getLogger().setLevel(logging.DEBUG)

import aidapy.hist as aph
import ROOT

if args.g:
    aph.json2hists(args.j,tree_name='ALL')

if args.t:
    print aph.sysband(ROOT.TFile('aida_histograms.root','READ'),'met_0j')
