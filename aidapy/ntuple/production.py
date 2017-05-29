from __future__ import print_function

import yaml
import subprocess
import os
import aidapy.meta as apm
import sys

aidapydir = str(os.getenv('AIDAPYDIR'))
yaml_file = aidapydir+'/data/production.yaml'
with open(yaml_file) as f:
    yaml_top = yaml.load(f)
atndir='/data/dukhep09/b/users/ddavis/top/at/v2430/mc/user.ddavis.'

def command(dsid='', tree_name='', out_file='', out_tree='', is_fast=False):
    base   = 'runAIDALoop --loop-alg --no-ttrv-warning -a '+atndir
    fof    = '.*_s*output.root'
    if is_fast: fof = '.*_a*output.root'
    pieces = [base+dsid+fof,'-n',tree_name,'-o','outs2/'+out_file,'--override-outtree-name',out_tree]
    return ' '.join(pieces)

def unravel_dsids(arr):
    dsids = []
    for entry in arr:
        if isinstance(entry,list):
            for dsid in range(entry[0],entry[1]+1):
                dsids.append(dsid)
        else:
            dsids.append(entry)
    return dsids

def chunks(l, n):
    n = max(1, n)
    return (l[i:i+n] for i in xrange(0, len(l), n))

def runAIDALoop(tree_name, dry=False):
    commands_to_run = []
    for process in yaml_top:
        full_dict = yaml_top[process]['FULL']
        if 'FAST' in yaml_top[process] and tree_name == 'nominal':
            fast_dict = yaml_top[process]['FAST']
        else:
            fast_dict = {}
        for sample_type, samples in full_dict.items():
            if tree_name == 'nominal':
                outtreename = samples['OutTreeName']
            else:
                outtreename = tree_name
            dsids = unravel_dsids(samples['DSIDs'])
            for dsid in dsids:
                commands_to_run.append(command(str(dsid),
                                               tree_name,
                                               process+'_'+str(dsid)+'.root',
                                               outtreename,
                                               False))
        for sample_type, samples in fast_dict.items():
            dsids = unravel_dsids(samples['DSIDs'])
            for dsid in dsids:
                commands_to_run.append(command(str(dsid),
                                               tree_name,
                                               process+'_'+str(dsid)+'.root',
                                               samples['OutTreeName'],
                                               True))
    #newchunks = chunks(commands_to_run,8)
    #for c in list(newchunks):
    #    print("###")
    #    for cc in c:
    #        print(cc)
    #    if dry: hashbang = '#'
    #    else: hashbang = ''
    #    processes = [subprocess.Popen(hashbang+cc, shell=True) for cc in c]
    #    for p in processes: p.wait()
    for com in commands_to_run:
        if dry:
            com = '#'+com
        else:
            pass
        #print(com)
        subprocess.call('echo "'+com+'"',shell=True)
        subprocess.call(com,shell=True)

def main(args):
    runAIDALoop('nominal',dry=('dry' in args))
    if 'systematics' in args:
        for sys in apm._systematic_trees:
            runAIDALoop(sys,dry=('dry' in args))

if __name__ == '__main__':
    main(sys.argv[1:])
