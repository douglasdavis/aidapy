#!/usr/bin/env bash

if [ -z "$ROOTCOREBIN" ]; then
    echo "Warning: ROOTCOREBIN env var not set"
    echo "Setting up a standalone ROOT release"
    echo "If this is not your desired setup, start over with your RootCore area set up."
    lsetup root
fi

lsetup 'sft releases/LCG_88/numpy/1.11.0'
lsetup 'sft releases/LCG_88/root_numpy/4.6.0'
lsetup 'sft releases/LCG_88/scipy/0.18.1'
lsetup 'sft releases/LCG_88/matplotlib/1.5.1'

AIDAPYDIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
export PYTHONPATH=$PYTHONPATH:$AIDAPYDIR
