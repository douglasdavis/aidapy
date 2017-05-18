from __future__ import print_function

import yaml
from subprocess import Popen
import os
import aidapy.meta as apm

aidapydir = str(os.getenv('AIDAPYDIR'))
yaml_file = aidapydir+'/data/production.yaml'
atndir='/data/dukhep09/b/users/ddavis/top/at/v2430/mc/user.ddavis.'

def runAIDALoop(tree_name, dry=False):
    command  = 'runAIDALoop --loop-alg --no-ttrv-warning'
    command += ' -n ' + tree_name
    command += ' -a ' + atndir
    with open(yaml_file) as f:
        yaml_top = yaml.load(f)

    commands_to_run = []
    for process, full_fast_dict in yaml_top.items():
        full_dict = full_fast_dict['FULL']
        if 'FAST' in full_fast_dict:
            fast_dict = full_fast_dict['FAST']
        else:
            fast_dict = None

        if tree_name == 'nominal':
            for key, sampdict in full_dict.items():
                outtree = sampdict['TreeName']
                treecom = '--override-outtree-name '+outtree
                for entry in sampdict['DSIDs']:
                    if isinstance(entry,list):
                        for dsid in range(entry[0],entry[1]+1):
                            out = process+'.'+key+'_'+str(dsid)+'.root'
                            if process == 'ttbar':
                                out = 'ttbar_all.root'
                            out = '-o '+out
                            c = command+str(dsid)+'.*_s*output.root '+out+' '+treecom
                            commands_to_run.append(c)
                    else:
                        dsid = entry
                        out = process+'.'+key+'_'+str(dsid)+'.root'
                        if process == 'ttbar':
                            out = 'ttbar_all.root'
                        out = '-o '+out
                        c = command+str(dsid)+'.*_s*output.root '+out+' '+treecom
                        commands_to_run.append(c)

        else:
            for key, sampdict in full_dict.items():
                if key == 'main':
                    for entry in sampdict['DSIDs']:
                        if isinstance(entry,list):
                            for dsid in range(entry[0],entry[1]+1):
                                out = process+'.'+key+'_'+str(dsid)+'.root'
                                if process == 'ttbar':
                                    out = 'ttbar_all.root'
                                out = '-o '+out
                                c = command+str(dsid)+'*_s*output.root '+out
                                commands_to_run.append(c)
                        else:
                            dsid = entry
                            out = process+'.'+key+'_'+str(dsid)+'.root'
                            if process == 'ttbar':
                                out = 'ttbar_all.root'
                            out = '-o '+out
                            c = command+str(dsid)+'*_s*output.root '+out
                            commands_to_run.append(c)

        if fast_dict is not None and tree_name == 'nominal':
            for key, sampdict in fast_dict.items():
                outtree = sampdict['TreeName']
                treecom = '--override-outtree-name '+outtree
                for entry in sampdict['DSIDs']:
                    if isinstance(entry,list):
                        for dsdid in range(entry[0],entry[1]+1):
                            out = process+'.'+key+'_'+str(dsid)+'.root'
                            if process == 'ttbar':
                                out = 'ttbar_all.root'
                            c = command+str(dsid)+'.*_a*output.root '+out+' '+treecom
                            commands_to_run.append(c)
                    else:
                        dsid = entry
                        out = process+'.'+key+'_'+str(dsid)+'.root'
                        if process == 'ttbar':
                            out = 'ttbar_all.root'
                        out = '-o '+out
                        c = command+str(dsid)+'.*_a*output.root '+out+' '+treecom
                        commands_to_run.append(c)

    def chunks(l, n):
        n = max(1, n)
        return (l[i:i+n] for i in xrange(0, len(l), n))
    newchunks = chunks(commands_to_run,4)
    for c in list(newchunks):
        print("###")
        for cc in c:
            print(cc)
        if dry: hashbang = '#'
        else: hashbang = ''
        processes = [Popen(hashbang+cc, shell=True) for cc in c]
        for p in processes: p.wait()

for sys in apm._systematic_trees:
    runAIDALoop(sys, dry=True)
