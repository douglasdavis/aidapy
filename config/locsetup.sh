#!/usr/bin/env bash

export AIDAPYDIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )/.."
export PYTHONPATH=$PYTHONPATH:$AIDAPYDIR
export PATH=$PATH:$AIDAPYDIR/scripts
