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
and specify a YAML configuration file with the ``-y (--yaml-config)``
option. Example:

.. code-block:: none

   $ aida.py -g -y /path/to/myconfig.yaml

This will create a file ``aida_histograms.root`` in your current
directory. By default all tree systematic histograms and weight
systematic histograms are generated.

TO BE UPDATED

Plot Generation
---------------
To generate plots from a ROOT file containing histograms, run with the
``-p`` option.

**UNDER DEVELOPMENT.**

API Documentation
=================

API documentation can be found here: http://ddavis.web.cern.ch/ddavis/aidapy/api.html
