FROM gcc:4.9

MAINTAINER Santiago Videla <santiago.videla@gmail.com>

### adapted from https://hub.docker.com/r/continuumio/miniconda/

RUN apt-get update --fix-missing && apt-get install -y wget bzip2 ca-certificates \
    libglib2.0-0 libxext6 libsm6 libxrender1 \
    git mercurial subversion

RUN echo 'export PATH=/opt/conda/bin:$PATH' > /etc/profile.d/conda.sh && \
    wget --quiet https://repo.continuum.io/miniconda/Miniconda2-4.1.11-Linux-x86_64.sh && \
    /bin/bash /Miniconda2-4.1.11-Linux-x86_64.sh -b -p /opt/conda && \
    rm Miniconda2-4.1.11-Linux-x86_64.sh

RUN apt-get install -y curl grep sed dpkg && \
    TINI_VERSION=`curl https://github.com/krallin/tini/releases/latest | grep -o "/v.*\"" | sed 's:^..\(.*\).$:\1:'` && \
    curl -L "https://github.com/krallin/tini/releases/download/v${TINI_VERSION}/tini_${TINI_VERSION}.deb" > tini.deb && \
    dpkg -i tini.deb && \
    rm tini.deb && \
    apt-get clean

ENV PATH /opt/conda/bin:$PATH

# http://bugs.python.org/issue19846
# > At the moment, setting "LANG=C" on a Linux system *fundamentally breaks Python 3*, and that's not OK.
ENV LANG C.UTF-8

###

RUN conda config --set show_channel_urls true
RUN conda install --no-update-dependencies -y caspo -c bioasp -c svidela -c conda-forge

ENV PYTHONWARNINGS=ignore
ENTRYPOINT ["caspo"]
CMD ["--help"]
