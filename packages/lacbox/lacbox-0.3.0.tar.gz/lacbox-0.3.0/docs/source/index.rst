.. lacbox documentation master file, created by
   sphinx-quickstart on Tue Sep  6 07:23:40 2022.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to lacbox's documentation!
==================================

*lacbox* is a python module with a collection of methods useful for the *Loads, Aerodynamic and Control of Wind Turbines* course (46320).  

It mostly contain methods for reading and writing HAWC2 related files, but also methods that are useful doing the design of the new rotor.

Installation
------------
It is recomented to install *lacbox* via pip:

.. code-block:: shell

   pip install lacbox

If this do not work, the repo should be cloned and installed with the command: :code:`pip install -e .` standing in the folder containing the *setup.py* file.

You can upgrade your installation of lacbox

.. code-block:: shell

   pip install --upgrade lacbox

.. toctree::
   :maxdepth: 3
   :caption: Contents:

   IO
   rotor_design
   htc
   api

