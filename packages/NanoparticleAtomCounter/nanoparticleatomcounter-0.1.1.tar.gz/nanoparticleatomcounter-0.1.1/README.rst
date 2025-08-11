Nanoparticle Atom Counter
=========================

Treating a supported nanoparticle as a spherical cap, NanoparticleAtomCounter rapidly estimates the number of **Total**, **Surface**, **Perimeter**, and **Interfacial** atoms (see below).
Only two inputs are mandatory: the radius and contact angle, readily obtainable from Transmission Electron Microscopy (TEM) images.



.. figure:: https://raw.githubusercontent.com/giolajide/NanoparticleAtomCounter/main/Nanoparticle_Legend.png 
   :width: 450
   :alt: Atom types discriminated
   :align: center



Can be used on the web app_ or on a command line.




Requirements
------------

* numpy>=1.20,<2.3
* pandas>=1.4
* streamlit>=1.4,<2
* openpyxl>=3.1.0
* xlrd>=2.0.1


For testing, these are also required

* pytest>=8,<9
* ase>=3.22.0,<3.25
* tqdm<=4.67.1
* joblib<=1.5.1
* ascii-colors



Installation
------------

First create and activate a new environment::

    mamba create --name env_name "python>=3.10,<3.15"
    mamba activate env_name

To install the latest version::

    pip install NanoparticleAtomCounter
    #pip install NanoparticleAtomCounter[test] to be able to run tests

Alternatively::

    git clone git@github.com:szilvasi-group/NanoparticleAtomCounter.git
    cd NanoparticleAtomCounter/
    pip install -e .
    #pip install -e ".[test]" to be able to run tests



Usage
-------

**1) Prepare your input CSV**

Upload a ``.csv`` with these headers:

::

    r (A), R (A), Theta, Element, Interface Facet, Surface Facet

Definitions:

- ``r (A)`` = footprint radius (in Angstrom); ``R (A)`` = radius of curvature (in Angstrom)

**r vs R**

========== ==========
|acute|    |obtuse|
========== ==========

.. |acute| image:: https://raw.githubusercontent.com/giolajide/nanoparticleatomcounter/main/Acute.png
   :width: 340
   :alt: Acute theta

.. |obtuse| image:: https://raw.githubusercontent.com/giolajide/nanoparticleatomcounter/main/Obtuse.png
   :width: 340
   :alt: Obtuse theta


- Provide either ``r (A)`` or ``R (A)`` (if both are present, ``R (A)`` is ignored).
- ``Theta`` = contact angle (in degrees)
- ``Element`` = chemical symbol of the element that comprises the nanoparticle, e.g. ``Cr``
- ``Interface Facet`` and ``Surface Facet`` are OPTIONAL; leave blank if unknown.
    - ``Interface Facet`` = facet at the nanoparticle-support interface, e.g. ``(1,1,1)``
    - ``Surface Facet`` = dominant facet at the nanoparticle-gas/vacuum interface, e.g. ``(1,0,0)``

- Here's a sample input file_



**2) Use the web app**

Upload your input file and download the output.

OR


**2) Use the command line**

::

    nanoparticle-atom-count -i input_file.csv -o output_file.csv


Testing
-------

If you have it installed with the tests, then run the following test and please let me know if there are any errors::

    atom-count-test



Contact
-------

Any problems or questions?

* Email me at giolajide@crimson.ua.edu
* Or raise an issue right here_




.. _app: https://nanoparticle-atom-counting.streamlit.app
.. _here: https://github.com/szilvasi-group/NanoparticleAtomCounter/issues
.. _file: https://github.com/giolajide/NanoparticleAtomCounter/blob/main/sample_input.csv
