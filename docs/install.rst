.. toctree::
   :maxdepth: 2

Install
=======

In what follows, we assume you are installing **caspo** on a UNIX-like system.
Towards that end, we describe two alternative ways to install **caspo**.
Nonetheless, other settings may be possible depending on your platform.
Essentially, you will need to have python 2.7.x and some of the standard scientific python packages installed, namely, `pandas`_, `scipy`_, `scikit-learn`_, `networkx`_, `seaborn`_, and `joblib`_. Also, unless you decide to use the Docker image (see :ref:`using-docker`), you will need to compile the answer set programming solver `clingo`_ in order to build its python module and installed it in your python environment.

.. _pandas: http://pandas.pydata.org
.. _scipy: http://www.scipy.org
.. _scikit-learn: http://www.scikit-learn.org
.. _networkx: http://networkx.github.io
.. _seaborn: http://stanford.edu/~mwaskom/software/seaborn/
.. _joblib: https://pythonhosted.org/joblib/
.. _`clingo`: http://potassco.sourceforge.net/#clingo


.. _using-docker:

Using Docker (for end-users)
----------------------------

Follow the instructions to install Docker at http://www.docker.com.
Once you have installed Docker on your computer, you can use the **caspo** docker image as follows.
First you need to pull the image with::

    $ docker pull bioasp/caspo
    
That's it. Now, you should be able to run **caspo** with docker. By default, if no arguments are given, the help message will be shown::

    $ docker run bioasp/caspo
    usage: caspo [-h] [--quiet] [--out O] [--version]
                 {learn,classify,predict,design,control,visualize,test} ...

    Reasoning on the response of logical signaling networks with ASP

    optional arguments:
      -h, --help            show this help message and exit
      --quiet               do not print anything to standard output
      --out O               output directory path (Default to './out')
      --version             show program's version number and exit

    caspo subcommands:
      for specific help on each subcommand use: caspo {cmd} --help

      {learn,classify,predict,design,control,visualize,test}
      
Any argument given after *bioasp/caspo* will be consumed by **caspo**. For example, you can ask for help on a subcommand by running::

      $ docker run bioasp/caspo learn --help
      usage: caspo learn [-h] [--threads T] [--conf C] [--fit F] [--size S]
                         [--factor D] [--discretization T] [--length L]
                         pkn midas time

      positional arguments:
        pkn                 prior knowledge network in SIF format
        midas               experimental dataset in MIDAS file
        time                time-point to be used in MIDAS

      optional arguments:
        -h, --help          show this help message and exit
        --threads T         run parallel search with given number of threads
        --conf C            threads configurations (Default to many)
        --fit F             tolerance over fitness (Default to 0)
        --size S            tolerance over size (Default to 0)
        --factor D          discretization over [0,D] (Default to 100)
        --discretization T  discretization function: round, floor, ceil (Default to
                            round)
        --length L          max length for conjunctions (hyperedges) (Default to 0;
                            unbounded)

Usually, **caspo** will need to read and writes files to do their work. A possible way to this using docker is as follows. For safety, we recommend to use an empty directory::

    $ mkdir caspo-wd && cd caspo-wd

Next, we will run docker, mount the current directory into the container, and use it as the working directory for running **caspo test**::

    $ docker run --rm -v $PWD:/caspo-wd -w /caspo-wd bioasp/caspo test

    Testing caspo subcommands using test case Toy.

    Copying files for running tests:
    	Prior knowledge network: pkn.sif
    	Phospho-proteomics dataset: dataset.csv
    	Experimental setup: setup.json
    	Intervention scenarios: scenarios.csv

    $ caspo --out out learn out/pkn.sif out/dataset.csv 10 --fit 0.1 --size 5

    Optimum logical network learned in 0.0183s
    Optimum logical networks has MSE 0.1100 and size 7
    5 (nearly) optimal logical networks learned in 0.0082s
    Weighted MSE: 0.1100

    $ caspo --out out classify out/networks.csv out/setup.json out/dataset.csv 10

    Classifying 5 logical networks...
    Input-Output logical behaviors: 3
    Weighted MSE: 0.1100

    $ caspo --out out design out/behaviors.csv out/setup.json

    1 optimal experimental designs in 0.0043s

    $ caspo --out out predict out/behaviors.csv out/setup.json

    Computing all predictions and their variance for 3 logical networks...

    $ caspo --out out control out/networks.csv out/scenarios.csv

    3 optimal intervention strategies found in 0.0047s

    $ caspo --out out visualize --pkn out/pkn.sif --networks out/networks.csv --setup out/setup.json
    
If everything works as expected, you should find a directory named *out* in the current directory having all the output files generated by **caspo**. 

Finally, if you don't want to write the full docker command every time you run **caspo**, you may want
to create a shell script or alias as a shortcut. 
For example, you may want to create a file in your working directory named *caspo* and with the following content::

    #!/bin/sh
    docker run --rm -v $PWD:/caspo-wd -w /caspo-wd bioasp/caspo $@
    
Next, make the file executable::

    $ chmod a+x caspo

Now you can run **caspo** with::
    
    $ ./caspo

Using Anaconda (for software developers)
----------------------------------------

Follow the instructions to install Anaconda at http://www.anaconda.org.
Once you have installed Anaconda, you need to create a python environment having some standard scientific packages::

    $ conda create -n caspo-env pip ipython pandas scipy scikit-learn networkx seaborn joblib
    $ source activate caspo-env
    
Next, you need to compile the solver clingo 4.5.x which can be downloaded from its `sourceforge page <https://sourceforge.net/projects/potassco/files/clingo/>`_. 
After unpacking the sources, you will find detailed instructions in the INSTALL file for most popular platforms.
Note that you need to build the python module and make sure it's linked with the anaconda python environment you just created.
You may want to verify this by running::

    $ ipython
    Python 2.7.10 |Continuum Analytics, Inc.| (default, Oct 19 2015, 18:31:17)
    Type "copyright", "credits" or "license" for more information.

    IPython 4.0.0 -- An enhanced Interactive Python.
    ?         -> Introduction and overview of IPython's features.
    %quickref -> Quick reference.
    help      -> Python's own help system.
    object?   -> Details about 'object', use 'object??' for extra details.

    In [1]: import gringo
    In [2]: gringo.__version__
    Out[2]: '4.5.3'

Finally, install **caspo** using pip by running::
    
    $ pip install caspo
    
Now, you should be able to run **caspo**::

    $ caspo --help
    usage: caspo [-h] [--quiet] [--out O] [--version]
                 {learn,classify,predict,design,control,visualize,test} ...

    Reasoning on the response of logical signaling networks with ASP

    optional arguments:
      -h, --help            show this help message and exit
      --quiet               do not print anything to standard output
      --out O               output directory path (Default to './out')
      --version             show program's version number and exit

    caspo subcommands:
      for specific help on each subcommand use: caspo {cmd} --help

      {learn,classify,predict,design,control,visualize,test}

Ask for help on a subcommand by running for example::
    
    $ caspo learn --help
    usage: caspo learn [-h] [--threads T] [--conf C] [--fit F] [--size S]
                       [--factor D] [--discretization T] [--length L]
                       pkn midas time

    positional arguments:
      pkn                 prior knowledge network in SIF format
      midas               experimental dataset in MIDAS file
      time                time-point to be used in MIDAS

    optional arguments:
      -h, --help          show this help message and exit
      --threads T         run parallel search with given number of threads
      --conf C            threads configurations (Default to many)
      --fit F             tolerance over fitness (Default to 0)
      --size S            tolerance over size (Default to 0)
      --factor D          discretization over [0,D] (Default to 100)
      --discretization T  discretization function: round, floor, ceil (Default to
                          round)
      --length L          max length for conjunctions (hyperedges) (Default to 0;
                          unbounded)
    

Finally, run **caspo test** to make sure everything is working as expected::

    $ caspo test
    
    Testing caspo subcommands using test case Toy.

    Copying files for running tests:
    	Prior knowledge network: pkn.sif
    	Phospho-proteomics dataset: dataset.csv
    	Experimental setup: setup.json
    	Intervention scenarios: scenarios.csv

    $ caspo --out out learn out/pkn.sif out/dataset.csv 10 --fit 0.1 --size 5

    Optimum logical network learned in 0.0183s
    Optimum logical networks has MSE 0.1100 and size 7
    5 (nearly) optimal logical networks learned in 0.0082s
    Weighted MSE: 0.1100

    $ caspo --out out classify out/networks.csv out/setup.json out/dataset.csv 10

    Classifying 5 logical networks...
    Input-Output logical behaviors: 3
    Weighted MSE: 0.1100

    $ caspo --out out design out/behaviors.csv out/setup.json

    1 optimal experimental designs in 0.0043s

    $ caspo --out out predict out/behaviors.csv out/setup.json

    Computing all predictions and their variance for 3 logical networks...

    $ caspo --out out control out/networks.csv out/scenarios.csv

    3 optimal intervention strategies found in 0.0047s

    $ caspo --out out visualize --pkn out/pkn.sif --networks out/networks.csv --setup out/setup.json
    
If everything works as expected, you should find a directory named *out* in the current directory having all the output files generated by **caspo**.

