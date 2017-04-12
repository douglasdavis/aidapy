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

.. code-block:: bash

   $ source lxsetup.sh

This will simply set up a proper python path and set up some extra
python packages through the ``sft.cern.ch`` ``cvmfs`` area.

In a local environment

.. code-block:: bash

   $ source locsetup.sh

This will set up the proper python path and executable path. You must
have ROOT, numpy, scipy, and matplotlib installed.

To install the python library into your python site-packages (not
necessary but yields standard python access to the aidapy API):

.. code-block:: bash

   $ pip install .

Getting started
===============

After setting up aidapy, an executable script is provided for running
different parts of the library. To see the list of options:

.. code-block:: bash

   $ aida.py --help

Keep reading for more details.

Histogram Generation
--------------------

To generate histograms from AIDA trees (the output of AIDALoop's
TopLoop algorithm), run with the ``-g (--generate-histograms)`` option
and specify a JSON configuration file with the ``-j (--json)``
option. Example:

.. code-block:: bash

   $ aida.py -g -j /path/to/myconfig.json

This will create a file ``aida_histograms.root`` in your current
directory. By default all tree systematic histograms and weight
systematic histograms are generated.


There are example JSON configurations in the ``share`` directory. The
required ingredients:

- ``procs``: List of processes to generate histograms for.

  - See list of available here: http://ddavis.web.cern.ch/ddavis/aidapy/api/aidapy.html#aidapy.meta.get_dsids

- ``datafiles``: List of ROOT files containing real data AIDA ntuples
- ``mcpath``: path to a directory containing MC files, the files **must be named <dsid>.root**
- ``lumi``: the integrated luminosity to scale the MC histograms
- ``histograms``: list of JSON objects defining each histogram to be made.

If you're using the Duke ATLAS machines - the ``dukeatl.json`` file
should work by default (you can just copy it and add more histograms).

A more detailed example:

.. code-block:: bash

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

API documentation can be found here: http://cern.ch/ddavis/aidapy/api/aidapy.html

Note
====

This project has been set up using PyScaffold 2.5.7. For details and usage
information on PyScaffold see http://pyscaffold.readthedocs.org/.
