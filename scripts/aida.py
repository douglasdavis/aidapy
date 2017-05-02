#!/usr/bin/env python

import sys, os
AIDAPYDIR = str(os.environ.get('AIDAPYDIR'))

import argparse
parser = argparse.ArgumentParser(
    description='AIDA histogramming and plotting'
)
parser.add_argument('-g','--generate-histograms',action='store_true',dest='gen_hists',default=False,
                    help='Flag to generate histograms and store in file')
parser.add_argument('-p','--generate-plots',dest='gen_plots',nargs='+',type=str,
                    help='Make plots (HARD CODED UNDER CONSTRUCTION')
parser.add_argument('-j','--json',type=str,dest='json_file',default=AIDAPYDIR+'/data/dukeatl.json',
                    help='JSON configuration file for histogram generation')
parser.add_argument('-n','--tree-name',type=str,dest='tree_name',default='ALL',
                    help='Name of AIDA tree to generate histograms from (ALL runs all of them)')
parser.add_argument('-o','--out-file',type=str,dest='out_file',default='aida_histograms.root',
                    help='Name of output file')
parser.add_argument('-t','--tests',action='store_true',dest='tests',default=False,
                    help='Run some tests')

args = parser.parse_args()
if len(sys.argv) < 2:
    parser.print_help()
    exit(0)

import aidapy.hist as aph
import aidapy.plot as app
import ROOT

if args.gen_hists:
    aph.json2hists(args.json_file,outfilename=args.out_file,tree_name=args.tree_name)

if args.tests:
    print('Doesn\'t do anything')

if args.gen_plots:
    for p in args.gen_plots:
        app.hplot_mpl(ROOT.TFile('aida_histograms.root','read'),p)
