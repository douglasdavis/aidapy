======
aidapy
======


AIDA (An Inclusive Dilepton Analysis) python library


Description
===========

This package is supplies a python interface to handle some tasks in
AIDA. It supplies a complete API for flexibility and also a python
script for handling common tasks.

Setup
=====

Clone the repository:
https://gitlab.cern.ch/atlas-aida/aidapy

To set up in an environment connected with ATLAS ``cvmfs`` directories
(``lxplus`` machines or ``atl0XX`` machines at Duke).

.. code-block:: none

   $ source config/lxsetup.sh

This will simply set up a proper python path and set up some extra
python packages through the ``sft.cern.ch`` ``cvmfs`` area.

In a local environment

.. code-block:: none

   $ source config/locsetup.sh

This will set up the proper python path and executable path. You must
have ROOT, numpy, scipy, and matplotlib installed.

To install the python library into your python site-packages (not
necessary but yields standard python access to the aidapy API):

.. code-block:: none

   $ pip install .

Getting started
===============

After setting up aidapy, an executable script is provided for running
different parts of the library. To see the list of options:

.. code-block:: none

   $ aida.py --help

Keep reading for more details.

Histogram Generation
--------------------

To generate histograms from AIDA trees (the output of AIDALoop's
TopLoop algorithm), run with the ``-g (--generate-histograms)`` option
and specify a JSON configuration file with the ``-j (--json)``
option. Example:

.. code-block:: none

   $ aida.py -g -j /path/to/myconfig.json

This will create a file ``aida_histograms.root`` in your current
directory. By default all tree systematic histograms and weight
systematic histograms are generated.


There are example JSON configurations in the ``data`` directory. The
required ingredients:

- ``procs``: List of processes to generate histograms for.

  - See list of available here:
    http://ddavis.web.cern.ch/ddavis/aidapy/api.html#aidapy.meta.get_dsids

- ``files``: a plain text file containing a list of ROOT files
  containing AIDA ntuples. The files listed here are not necessarily
  all used, aidapy scans the metadata of the files and sorts through
  them based on which processes are requests in the ``procs`` option.
- ``lumi``: the integrated luminosity to scale the MC histograms
- ``histograms``: list of JSON objects defining each histogram to be made.

If you're using the Duke ATLAS machines - the ``dukeatl.json`` file
should work by default (you can just copy it and add more histograms).

A more detailed example:

.. code-block:: none

   $ aida.py -g -j /path/to/myconfig.json -o histograms.root -n EG_RESOLUTION_ALL__1up

this command will create a file ``histograms.root`` and only generate
histograms for the tree systematic ``EG_RESOLUTION_ALL__1up``. You can
add more histograms by declarning the same output file with a
different tree name. Or if you don't include a tree name, all
remaining systematics that aren't in the file will be generated.

Plot Generation
---------------
To generate plots from a ROOT file containing histograms, run with the
``-p`` option.

**UNDER DEVELOPMENT.**

API Documentation
=================

API documentation can be found here: http://ddavis.web.cern.ch/ddavis/aidapy/api.html
