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

To set up in an ``lxplus`` like environment

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

Some more details:

Histogram Generation
--------------------
To generate histograms from AIDA trees (the output of AIDALoop's loop
TopLoop algorithm), run with the ``-g (--generate-histograms)`` option
and specify a JSON configuration file. There are example
configurations in the ``share`` directory. The required ingrediants:

- ``procs``: List of processes to generate histograms for. See list of available here:
http://ddavis.web.cern.ch/ddavis/aidapy/api/aidapy.html#aidapy.meta.get_dsids
- ``datafiles``: List of ROOT files containing real data AIDA ntuples
- ``mcpath``: path to a directory containing MC files, the files **must be named <dsid>.root**
- ``lumi``: the integrated luminosity to scale the MC histograms
- ``histograms``: list of JSON objects defining each histogram to be made.

Plot Generation
---------------
To generate plots from a ROOT file containing histograms, run with the
``-p`` option. **UNDER DEVELOPMENT.**

API Documentation
=================

API documentation can be found here: http://cern.ch/ddavis/aidapy/api/aidapy.html

Note
====

This project has been set up using PyScaffold 2.5.7. For details and usage
information on PyScaffold see http://pyscaffold.readthedocs.org/.
