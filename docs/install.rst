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

*NOTE: Depending on your platform and whether you decide to use the system's python or a virtual environment,
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

