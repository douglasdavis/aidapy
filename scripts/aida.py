#!/usr/bin/env python

import sys, os
AIDAPYDIR = str(os.environ.get('AIDAPYDIR'))

import argparse
parser = argparse.ArgumentParser(
    description='AIDA histogramming and plotting'
)
parser.add_argument('-g','--generate-histograms',action='store_true',dest='gen_hists',default=False,
                    help='Flag to generate histograms and store in file')
parser.add_argument('-y','--yaml-config',dest='yaml_config',type=str,
                    default=AIDAPYDIR+'/data/template.yaml',
                    help='Path to YAML config')
parser.add_argument('-p','--generate-plots',dest='gen_plots',nargs='+',type=str,
                    help='Make plots (HARD CODED UNDER CONSTRUCTION)')
parser.add_argument('-o','--out-file',type=str,dest='out_file',default='aida_histograms.root',
                    help='Name of output file')

args = parser.parse_args()
if len(sys.argv) < 2:
    parser.print_help()
    exit(0)

import aidapy.hist as aph
import aidapy.plot as app
import ROOT

if args.gen_hists:
    aph.generate_hists(args.yaml_config, output=args.out_file)

if args.gen_plots:
    for p in args.gen_plots:
        app.hplot_mpl(ROOT.TFile('aida_histograms.root','read'),p)
