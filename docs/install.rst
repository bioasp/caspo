Install
=======

In what follows we describe three alternative ways to install **caspo**:

* :ref:`using-docker`
* :ref:`using-anaconda`
* :ref:`using-pip`

Note that using pip requires the user to install all dependencies manually.
Since installing such dependecies requires basic skills on how to compile and deploy third-party python packages it is only recommended for experienced users.
Therefore, we recommend less experienced users to use either Docker or Anaconda.

.. _`clingo`: http://potassco.sourceforge.net/#clingo


.. _using-docker:

Using Docker
------------

Follow the instructions to install Docker at http://docs.docker.com.
Once you have installed Docker on your computer, you can use the **caspo** docker image as follows.
First you need to pull the image with::

    $ docker pull bioasp/caspo

That's it. Now, you should be able to run **caspo** with docker.
Usually, **caspo** will need to read and writes files to do their work.
A possible way to this using docker is as follows.
For safety, we recommend to use an empty directory::

    $ mkdir caspo-wd && cd caspo-wd

Next, let's take a look to the command needed to run docker, mount the current directory (*caspo-wd*) into the docker container, and use it as the working directory for running **caspo**::

    $ docker run --rm -v $PWD:/caspo-wd -w /caspo-wd bioasp/caspo

If you don't want to write the full docker command every time you run **caspo**, you may want to create a shell script or alias as a shortcut.
For example, you may want to create a file in your working directory named *caspo* and with the following content::

    #!/bin/sh
    docker run --rm -v $PWD:/caspo-wd -w /caspo-wd bioasp/caspo $@

Next, make the file executable::

    $ chmod a+x caspo

Now you can run **caspo** with just::

    $ ./caspo

Next, go to :ref:`testing-install`.

.. _using-anaconda:

Using Anaconda
--------------

*NOTE: In order for this method to work, the standard C/C++ libraries must be installed in your system.
In Linux you need to have gcc >= 4.9 while in OS X 10.9+ you need to install Xcode and the command line tools.*

Follow the instructions to install Anaconda at https://www.continuum.io/downloads.
Next, download the file :download:`environment.yml <../environment.yml>` and use it to create a conda environment where **caspo** will be installed::

    $ conda env create --file environment.yml
    Using Anaconda Cloud api site https://api.anaconda.org
    Fetching package metadata ...............
    Solving package specifications: ..........
    ...
    Linking packages ...
    [      COMPLETE      ]|####################################################| 100%
    #
    # To activate this environment, use:
    # $ source activate caspo-env
    #
    # To deactivate this environment, use:
    # $ source deactivate
    #

That's it. Now, you should be able to run **caspo** within the created environment.
Note that you need to *activate* the environment every time you open a new terminal.

Next, go to :ref:`testing-install`.

.. _using-pip:

Using pip
---------
*NOTE: Depending on your platform and whether you use the system's python or a virtual environment,
this method may require you to install additional compilers and libraries beforehand.*

Essentially, you will need to have python 2.7.x and some of the standard scientific python packages installed.
Download the file :download:`requirements.txt <../requirements.txt>` and install **caspo** by running::

    $ pip install -r requirements.txt

Alternatively, you could download **caspo** sources and after unpacking run::

    $ python setup.py install

Note that installing **caspo** in this way **does not** force the installation of any of the runtime dependencies.
In other words, you take full responsibility of installing all required packages to run **caspo** successfully.

Also, the python module of the answer set programming solver `clingo`_ must be available in the PYTHONPATH.
After unpacking clingo sources, you will find detailed instructions about how to compile and build the
python module in the INSTALL file.

Next, go to :ref:`testing-install`.

.. _testing-install:

Testing your installation
--------------------------

Once **caspo** is installed you can test the installation as follows.
To start with, you can ask for help::

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

A more interesting test is to run **caspo test** to make sure all subcommands are working::

    $ caspo test --help
    usage: caspo test [-h] [--threads T] [--conf C]
                      [--testcase {Toy,LiverToy,LiverDREAM,ExtLiver}]

    optional arguments:
      -h, --help            show this help message and exit
      --threads T           run clingo with given number of threads
      --conf C              threads configurations (Default to many)
      --testcase {Toy,LiverToy,LiverDREAM,ExtLiver}
                            testcase name

This subcommand will run all subcommands in **caspo** using different testcases (see ``--testcase`` argument)::

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

    $ caspo --out out visualize --pkn out/pkn.sif --setup out/setup.json
            --networks out/networks.csv --midas out/dataset.csv 10
            --stats-networks=out/stats-networks.csv --behaviors out/behaviors.csv
            --designs=out/designs.csv --predictions=out/predictions.csv
            --strategies=out/strategies.csv --stats-strategies=out/stats-strategies.csv

If everything works as expected, you should find a directory named *out* in the current directory having all the output files generated by **caspo**.
