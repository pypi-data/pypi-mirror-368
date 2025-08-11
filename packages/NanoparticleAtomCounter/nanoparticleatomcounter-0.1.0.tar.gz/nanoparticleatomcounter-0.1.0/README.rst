Nanoparticle Atom Counter
=========================

Treating a supported nanoparticle as a spherical cap, NanoparticleAtomCounter rapidly estimates the number of **Total**, **Surface**, **Perimeter**, and **Interfacial** atoms (see below).
Only two inputs are needed: the radius and contact angle, readily obtainable from Transmission Electron Microscopy (TEM) images.

.. figure:: https://raw.githubusercontent.com/giolajide/nanoparticleatomcounter/main/Nanoparticle_Legend.png
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

Alternatively::

    git clone git@github.com:giolajide/nanoparticleatomcounter.git
    cd nanoparticleatomcounter
    pip install -e .


To also be able to run tests, install as::

    pip install NanoparticleAtomCounter[test]



Usage
-------

* To use on the web app_, upload your input file and download the output
* To use on a command line::

    nanoparticle-atom-counter --input input.csv --output output.csv



Testing
-------

If you have it installed with the tests, then please run the following test and let me know if there are any errors::

    atom-count-test



Contact
-------

Any problems or questions?

* Email me at giolajide@crimson.ua.edu
* Or raise an issue right here_




.. _app: https://nanoparticle-atom-counting.streamlit.app
.. _here: https://github.com/giolajide/nanoparticleatomcounting/issues
