from __future__ import print_function

import yaml
from subprocess import Popen
import os
import aidapy.meta as apm

def runAIDALoop_on_tree(yaml_file, tree_name='nominal', outpfx='.', dry=False,
                        atndir='/data/dukhep09/b/users/ddavis/top/at/v2430/mc/'):
    """
    Take the YAML file for organzing samples/DSIDs and execute the
    runAIDALoop executable accordingly This is hard coded for use on
    the Duke machines at CERN. It runs 4 operations in parallel at a
    time.

    Parameters
    ----------
    yaml_file: the YAML file organzing the processes and DSIDs.
    tree_name: the AIDA tree name to process.
    outpfx:    the output prefix tacked onto the output file names.
    atndir:    AnalysisTop ntuple directory.
    dry:       Only print commands, don't execute.
    """
    if tree_name == 'ALL':
        for tn in apm._systematic_trees:
            runAIDALoop_on_tree(yaml_file, tree_name=tn, outpfx=outpfx, dry=dry, atndir=atndir)
        runAIDALoop_on_tree(yaml_file, tree_name='nominal', outpfx=outpfx, dry=dry, atndir=atndir)
        exit('Done')

    command  = 'runAIDALoop --loop-alg --no-ttrv-warning'
    command += ' -n '+tree_name
    command += ' -a ' + atndir
    with open(yaml_file) as f:
        yaml_top = yaml.load(f)

    commands_to_run = []
    for process, vals1 in yaml_top.items():
        fullorfast = ['FULL','FAST']
        if tree_name != 'nominal':
            fullorfast = ['FULL']
        for fof in fullorfast:
            if   fof == 'FULL': simtag = '*_s*'
            elif fof == 'FAST': simtag = '*_a*'
            else: raise ValueError('impossible????')
            if fof in vals1:
                for samptype, vals2 in vals1[fof].items():
                    for entry in vals2['DSIDs']:
                        if isinstance(entry,list):
                            for i in range(entry[0],entry[1]+1):
                                outname = ' -o '+outpfx+'/'+str(i)+'_'+fof+'.root'
                                RUN = command+'user.ddavis.'+str(i)+'.'+simtag+'output.root '+outname
                                commands_to_run.append(RUN)
                        else:
                            i = entry
                            outname = ' -o '+outpfx+'/'+str(i)+'_'+fof+'.root'
                            RUN = command+'user.ddavis.'+str(i)+'.'+simtag+'output.root '+outname
                            commands_to_run.append(RUN)
    def chunks(l, n):
        n = max(1, n)
        return (l[i:i+n] for i in xrange(0, len(l), n))
    newchunks = chunks(commands_to_run,4)
    for c in list(newchunks):
        print("###")
        for cc in c:
            print(cc)
        if dry: hashbang = '#'
        if dry: hashbing = ''
        processes = [Popen(hashbang+cc, shell=True) for cc in c]
        for p in processes: p.wait()

if __name__ == '__main__':
    aidapydir = str(os.getenv('AIDAPYDIR'))
    runAIDALoop_on_tree(aidapydir+'/data/files.yaml', tree_name='ALL', dry=True)
