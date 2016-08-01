Install
=======

In what follows we describe two alternative ways to install **caspo**.
Nonetheless, other settings may be possible depending on your platform.
Essentially, you will need to have python 2.7.x and some of the standard scientific python packages installed, namely, `pandas`_, `scipy`_, `scikit-learn`_, `networkx`_, `seaborn`_, and `joblib`_. 

Also, unless you decide to use the Docker image (see :ref:`using-docker`), you will need to compile the answer set programming solver `clingo`_ in order to build its python module and installed it in your python environment.
Since this requires basic skills on how to compile and deploy a third-party python module, it is only recommended for software developers who are interested in using **caspo** via its application programming interface (API).
On the other hand, end-users only interested in using **caspo** via its command line interface (CLI) are recommended to use Docker.

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

Follow the instructions to install Docker at http://docs.docker.com
Once you have installed Docker on your computer, you can use the **caspo** docker image as follows.
First you need to pull the image with::

    $ docker pull bioasp/caspo
    
That's it. Now, you should be able to run **caspo** with docker. By default, if no arguments are given, the help message will be shown::

    $ docker run --rm bioasp/caspo
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

      $ docker run --rm bioasp/caspo learn --help
      usage: caspo learn [-h] [--threads T] [--conf C] [--fit F] [--size S]
                         [--factor D] [--discretization T] [--length L]
                         pkn midas time

      positional arguments:
        pkn                 prior knowledge network in SIF format
        midas               experimental dataset in MIDAS file
        time                time-point to be used in MIDAS

      optional arguments:
        -h, --help          show this help message and exit
        --threads T         run clingo with given number of threads
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

Next, we will run docker, mount the current directory into the container, and use it as the working directory for running **caspo test**. The subcommand *test* runs all other subcommands using examples distributed with the software::

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
    In [1]: import gringo

    In [2]: gringo.__version__
    Out[2]: '4.5.4'

If you are using Mac OSx and you find an error when trying to import gringo, you may want to take a look to the :ref:`known-issue`. 
Otherwise, you can continue installing **caspo**.

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
      --threads T         run clingo with given number of threads
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

.. _known-issue:

Known issue building clingo in Mac OSx
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

When clingo is compiled in Mac OSx, it may happen that instead of linking against the python instance in the Anaconda environment where you will install **caspo** afterwards, the python module is linked against the global python instance in your system.
In such a case, when you try to import gringo from the python instance in the Anaconda environment, you will get an error (typically a *Segmentation fault: 11*):

Hopefully, you can fix this issue in a few steps.

First, find the clingo python module (after compiling you should find it at *clingo-4.5.4-source/build/release/python/gringo.so*) and run::

    $ otool -L gringo.so
    gringo.so:
    	build/release/python/gringo.so (compatibility version 0.0.0, current version 0.0.0)
    	/System/Library/Frameworks/Python.framework/Versions/2.7/Python (compatibility version 2.7.0, current version 2.7.10)
    	/opt/local/lib/liblua.dylib (compatibility version 5.3.0, current version 5.3.1)
    	/usr/lib/libSystem.B.dylib (compatibility version 1.0.0, current version 1226.10.1)
    	/opt/local/lib/libtbb.dylib (compatibility version 0.0.0, current version 0.0.0)
    	/usr/lib/libc++.1.dylib (compatibility version 1.0.0, current version 120.1.0)
        
        
The output will actually depend on how you have compiled clingo (in particular, you may not see *liblua.dylib* or *libtbb.dylib*). 
In any case, the issue here is at the second line where we can see that the module was linked against the global python instance::

    /System/Library/Frameworks/Python.framework/Versions/2.7/Python (...)

Next you need to run::

    $ install_name_tool -change /System/Library/Frameworks/Python.framework/Versions/2.7/Python @loader_path/../../libpython2.7.dylib gringo.so

Now if you run again otool you should see something like::

    $ otool -L gringo.so
    gringo.so:
        build/release/python/gringo.so (compatibility version 0.0.0, current version 0.0.0)
        @loader_path/../../libpython2.7.dylib (compatibility version 2.7.0, current version 2.7.10)
        /opt/local/lib/liblua.dylib (compatibility version 5.3.0, current version 5.3.1)
        /opt/local/lib/libtbb.dylib (compatibility version 0.0.0, current version 0.0.0)
        /usr/lib/libc++.1.dylib (compatibility version 1.0.0, current version 120.1.0)
        /usr/lib/libSystem.B.dylib (compatibility version 1.0.0, current version 1225.1.1)


Finally, move the fixed gringo.so to the Anaconda environment's site-packages. 
If Anaconda is installed at your $HOME directory::

    $ mv gringo.so $HOME/anaconda/envs/caspo-env/lib/python2.7/site-packages/

Now, you should be able to import gringo from the python instance in the Anaconda environment::

    $ ipython
    In [1]: import gringo

    In [2]: gringo.__version__
    Out[2]: '4.5.4'
