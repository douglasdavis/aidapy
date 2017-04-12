#!/usr/bin/env bash

if [ -z "$ROOTCOREBIN" ]; then
    lsetup 'root 6.08.06-x86_64-slc6-gcc49-opt'
    lsetup 'sft releases/LCG_88/numpy/1.11.0'
    lsetup 'sft releases/LCG_88/root_numpy/4.6.0'
    lsetup 'sft releases/LCG_88/scipy/0.18.1'
    lsetup 'sft releases/LCG_88/matplotlib/1.5.1'
    lsetup 'sft releases/LCG_88/setuptools/20.1.1'

    export AIDAPYDIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
    export PYTHONPATH=$PYTHONPATH:$AIDAPYDIR
    export PATH=$PATH:$AIDAPYDIR/scripts
else
    echo "Error: ROOTCOREBIN is set."
    echo "Due to RootCore's ROOT version, we can't use root_numpy."
    echo "This should be fixed in the future."
    echo "For now, just set this up without an existing RootCore setup."
fi